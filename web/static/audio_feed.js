// Audio input for the browser: the built-in demo signal, an audio file, the microphone (only after a click), or the
// simulated features of launcher.py / macos_demo.py (no audio at all). Audio is cut into consecutive 1024-sample
// chunks at 44.1 kHz (config.json chunk_size / sample_rate) and each chunk goes through the AudioAnalyzer port, so the
// plugins receive the same features as from main.AudioProcessor. The analyser clock is the stream time of the chunk.
import { AudioAnalyzer, desktopFeatures } from './audio_analyzer.js';
import { demoSignal, RATE } from './demo_signal.js';

export const CHUNK = 1024;
let actx = null;
export function audioContext() {
  if (!actx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    try { actx = new AC({ sampleRate: RATE }); } catch { actx = new AC(); }
  }
  return actx;
}

let demoCache = null;
const demoLoop = () => (demoCache ||= demoSignal());

export async function decodeFile(file) {
  const ctx = audioContext();
  const buf = await ctx.decodeAudioData(await file.arrayBuffer());
  let mono = new Float32Array(buf.length);
  for (let c = 0; c < buf.numberOfChannels; c++) {
    const d = buf.getChannelData(c);
    for (let i = 0; i < d.length; i++) mono[i] += d[i] / buf.numberOfChannels;
  }
  if (buf.sampleRate !== RATE) {
    const off = new OfflineAudioContext(1, Math.ceil(buf.length * RATE / buf.sampleRate), RATE);
    const b = off.createBuffer(1, buf.length, buf.sampleRate);
    b.copyToChannel(mono, 0);
    const src = off.createBufferSource(); src.buffer = b; src.connect(off.destination); src.start();
    mono = (await off.startRendering()).getChannelData(0);
  }
  return mono;
}

// launcher.py / macos_demo.py fake_audio at time t (seconds).
export function simulatedFeatures(t) {
  return {
    amplitude: 0.5 + 0.3 * Math.sin(t * 2), beat_detected: (t % 1.2) < 0.1,
    dominant_frequency: 440 + 200 * Math.sin(t * 0.5),
    frequency_bands: { bass: 0.3 + 0.2 * Math.sin(t), mid: 0.4 + 0.3 * Math.sin(t * 1.5), treble: 0.2 + 0.1 * Math.sin(t * 2) },
  };
}

const SILENT = { amplitude: 0, frequency: 0, beat_detected: false };

export class AudioFeed {
  constructor() {
    this.level = 0.5; this.mode = 'desktop';
    this.kind = 'demo'; this.data = demoLoop(); this.loop = true; this.label = 'Demo signal';
    this.node = null; this.gain = null; this.mic = null; this.sound = false;
    this.next = 0; this.offset = 0; this.t0 = performance.now(); this.paused = false; this.ended = false;
    this.analyzer = new AudioAnalyzer(RATE, CHUNK); this.latest = SILENT;
  }

  position() {
    if (this.kind === 'mic') return actx.currentTime * actx.sampleRate;
    if (this.node) return (actx.currentTime - this.startAt) * RATE;
    return this.offset + (this.paused ? 0 : (performance.now() - this.t0) / 1000 * RATE);
  }

  // The features the plugins should see now (the latest analysed chunk, as AudioProcessor.get_audio_features).
  features() {
    if (this.paused) return this.latest;
    if (this.kind === 'sim') return (this.latest = simulatedFeatures(this.position() / RATE));
    if (this.ended) return (this.latest = SILENT);
    const due = Math.floor(this.position() / CHUNK);
    if (due < this.next) return this.latest;
    if (this.kind === 'mic') { this.next = due + 1; return (this.latest = this.analyse(this.micChunk(), due)); }
    if (due - this.next > 6) this.next = due - 6;
    for (; this.next <= due; this.next++) {
      const start = this.next * CHUNK;
      if (!this.loop && start + CHUNK > this.data.length) { this.ended = true; this.latest = SILENT; break; }
      const x = new Float64Array(CHUNK), g = this.kind === 'demo' ? this.level : 1;
      for (let j = 0; j < CHUNK; j++) x[j] = this.data[(start + j) % this.data.length] * g;
      this.latest = this.analyse(x, this.next);
    }
    return this.latest;
  }

  analyse(x, index) { return desktopFeatures(x, RATE, this.analyzer, 1000 + index * CHUNK / RATE, this.mode); }

  micChunk() {
    const f = new Float32Array(CHUNK);
    this.mic.analyser.getFloatTimeDomainData(f);
    return Float64Array.from(f);
  }

  stopNodes() {
    if (this.node) { try { this.node.stop(); } catch { /* already stopped */ } this.node.disconnect(); this.node = null; }
    if (this.mic) { this.mic.stream.getTracks().forEach(t => t.stop()); this.mic.source.disconnect(); this.mic = null; }
  }

  reset(kind, data, label, loop) {
    this.stopNodes();
    Object.assign(this, { kind, data, label, loop, next: 0, offset: 0, t0: performance.now(), ended: false, paused: false });
    this.analyzer = new AudioAnalyzer(RATE, CHUNK); this.latest = SILENT;
  }

  useDemo() { const s = this.sound; this.reset('demo', demoLoop(), 'Demo signal', true); if (s) this.play(); }
  useSim() { this.reset('sim', null, 'Simulated features', true); this.sound = false; }

  async useFile(file) {
    const data = await decodeFile(file);
    this.reset('file', data, file.name, false);
    this.play();
  }

  async useMic() {
    const ctx = audioContext();
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.reset('mic', null, 'Microphone', false);
    const source = ctx.createMediaStreamSource(stream), analyser = ctx.createAnalyser();
    analyser.fftSize = CHUNK;
    source.connect(analyser);   // not connected to the speakers
    this.mic = { stream, source, analyser };
    this.sound = false;
    await ctx.resume();
    this.next = Math.floor(this.position() / CHUNK);
  }

  play() {
    if (this.kind === 'mic' || this.kind === 'sim') return;
    const ctx = audioContext(), pos = this.position();
    if (this.node) { this.node.stop(); this.node.disconnect(); }
    const buf = ctx.createBuffer(1, this.data.length, RATE);
    const g = this.kind === 'demo' ? this.level : 1;
    buf.copyToChannel(Float32Array.from(this.data, v => v * g), 0);
    const node = ctx.createBufferSource();
    node.buffer = buf; node.loop = this.loop;
    this.gain ||= ctx.createGain();
    this.gain.connect(ctx.destination);
    node.connect(this.gain);
    node.start(0, (pos % this.data.length) / RATE);
    this.startAt = ctx.currentTime - pos / RATE;
    this.node = node; this.sound = true;
    ctx.resume();
  }

  mute() {
    if (!this.node) { this.sound = false; return; }
    this.offset = this.position(); this.t0 = performance.now();
    this.node.stop(); this.node.disconnect(); this.node = null;
    this.sound = false;
  }

  setLevel(v) { this.level = v; if (this.kind === 'demo' && this.node) this.play(); }

  setPaused(p) {
    if (p === this.paused) return;
    if (p) { this.offset = this.position(); if (actx && this.node) actx.suspend(); }
    else { this.t0 = performance.now(); if (actx && this.node) actx.resume(); }
    this.paused = p;
  }

  rateNote() {
    return this.kind === 'mic' && actx && actx.sampleRate !== RATE
      ? `The browser runs the microphone at ${actx.sampleRate} Hz, not 44,100 Hz, so FFT bins are slightly wider than on the desktop.` : '';
  }
}
