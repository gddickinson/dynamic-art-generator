// Port of utils/audio_utils.py AudioAnalyzer.analyze_audio and utils/desktop_features.py desktop_audio_features:
// the per-chunk audio features the desktop app hands to the plugins. Pure JS (no DOM); `now` replaces time.time()
// (the browser passes the stream time of the chunk). Checked against Python by audio.test.mjs.
import { rfftAbs } from './fft.js';

const hannCache = new Map();
function hann(n) {   // np.hanning(n)
  if (!hannCache.has(n)) {
    const w = new Float64Array(n);
    for (let i = 0; i < n; i++) w[i] = n === 1 ? 1 : 0.5 - 0.5 * Math.cos(2 * Math.PI * i / (n - 1));
    hannCache.set(n, w);
  }
  return hannCache.get(n);
}
const sum = a => { let s = 0; for (const v of a) s += v; return s; };
const median = a => { const s = [...a].sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const push = (arr, v, max) => { arr.push(v); if (arr.length > max) arr.shift(); };

export class AudioAnalyzer {
  constructor(sampleRate = 44100, windowSize = 1024) {
    this.sample_rate = sampleRate; this.window_size = windowSize;
    this.energy_history = []; this.beat_threshold = 1.5; this.last_beat_time = 0; this.min_beat_interval = 0.1;
    this.onset_threshold = 0.3; this.spectral_flux_history = [];
    this.tempo_history = []; this.estimated_tempo = 120; this.last_tempo_beat_time = null;
  }

  // analyze_frequency: [frequencies, |rfft(x * hanning)|]
  analyzeFrequency(x) {
    const n = x.length, w = hann(n), xw = new Float64Array(n);
    for (let i = 0; i < n; i++) xw[i] = x[i] * w[i];
    const mags = rfftAbs(xw), freqs = new Float64Array(mags.length);
    for (let k = 0; k < mags.length; k++) freqs[k] = k * this.sample_rate / n;   // np.fft.rfftfreq
    return [freqs, mags];
  }

  analyze(x, now) {
    if (x.length === 0) return emptyFeatures();
    let peak = 0, sq = 0;
    for (const v of x) { peak = Math.max(peak, Math.abs(v)); sq += v * v; }
    const rms = Math.sqrt(sq / x.length);
    const [freqs, mags] = this.analyzeFrequency(x);
    let pi = 0;
    for (let k = 1; k < mags.length; k++) if (mags[k] > mags[pi]) pi = k;
    const total = sum(mags);
    let centroid = 0;
    if (total !== 0) { let s = 0; for (let k = 0; k < mags.length; k++) s += freqs[k] * mags[k]; centroid = s / total; }
    const beat = this.detectBeat(sq, now);
    const onset = this.detectOnset(mags);
    this.updateTempo(beat, now);
    return {
      amplitude: peak, rms, dominant_frequency: freqs[pi], spectral_centroid: centroid, beat_detected: beat,
      onset_detected: onset, estimated_tempo: this.estimated_tempo, harmonicity: harmonicity(freqs, mags),
      spectral_rolloff: rolloff(freqs, mags, total), zero_crossing_rate: zcr(x), frequency_bands: bandsOf(freqs, mags),
    };
  }

  detectBeat(energy, now) {
    push(this.energy_history, energy, 43);
    if (this.energy_history.length < 20) return false;
    const last = this.energy_history.slice(-20), mean = sum(last) / 20;
    let v = 0; for (const e of last) v += (e - mean) ** 2;
    const threshold = mean + this.beat_threshold * Math.sqrt(v / 20);
    if (energy > threshold && now - this.last_beat_time > this.min_beat_interval) { this.last_beat_time = now; return true; }
    return false;
  }

  // Spectral flux of the windowed magnitudes (detect_onset recomputes the same FFT; the result is identical).
  detectOnset(mags) {
    if (this.spectral_flux_history.length === 0) { push(this.spectral_flux_history, mags, 10); return false; }
    const prev = this.spectral_flux_history[this.spectral_flux_history.length - 1];
    let flux = 0;
    for (let k = 0; k < Math.min(mags.length, prev.length); k++) flux += Math.max(0, mags[k] - prev[k]);
    push(this.spectral_flux_history, mags, 10);
    return flux > this.onset_threshold;
  }

  updateTempo(beat, now) {
    if (!beat) return;
    if (this.last_tempo_beat_time !== null) {
      const interval = now - this.last_tempo_beat_time;
      if (interval > 0.3 && interval < 2.0) { push(this.tempo_history, 60 / interval, 20); this.estimated_tempo = median(this.tempo_history); }
    }
    this.last_tempo_beat_time = now;
  }
}

function harmonicity(freqs, mags) {
  if (mags.length < 10) return 0;
  const peaks = [];
  for (let i = 1; i < mags.length - 1; i++) if (mags[i] > mags[i - 1] && mags[i] > mags[i + 1]) peaks.push([freqs[i], mags[i]]);
  if (peaks.length < 2) return 0;
  peaks.sort((a, b) => b[1] - a[1]);
  const f0 = peaks[0][0];
  if (f0 < 20) return 0;
  let strength = 0;
  for (const [f, m] of peaks.slice(1, 6)) {
    const r = f / f0;
    if (Math.abs(r - pyRound(r)) < 0.1) strength += m;
  }
  return Math.min(1, strength / sum(peaks.slice(0, 6).map(p => p[1])));
}

// Python round(): halves to even.
function pyRound(x) {
  const f = Math.floor(x), d = x - f;
  if (d > 0.5) return f + 1;
  if (d < 0.5) return f;
  return f % 2 === 0 ? f : f + 1;
}

function rolloff(freqs, mags, total) {
  if (mags.length === 0 || total === 0) return 0;
  let c = 0;
  for (let k = 0; k < mags.length; k++) { c += mags[k]; if (c >= 0.85 * total) return freqs[k]; }
  return freqs[freqs.length - 1];
}

function zcr(x) {
  if (x.length < 2) return 0;
  let z = 0;
  for (let i = 1; i < x.length; i++) z += Math.abs(Math.sign(x[i]) - Math.sign(x[i - 1]));
  return z / (2 * x.length);
}

function bandsOf(freqs, mags) {
  let b = 0, m = 0, t = 0;
  for (let k = 0; k < mags.length; k++) {
    if (freqs[k] <= 250) b += mags[k]; else if (freqs[k] <= 4000) m += mags[k]; else t += mags[k];
  }
  const tot = b + m + t;
  return tot > 0 ? { bass: b / tot, mid: m / tot, treble: t / tot } : { bass: b, mid: m, treble: t };
}

function emptyFeatures() {
  return { amplitude: 0, rms: 0, dominant_frequency: 0, spectral_centroid: 0, beat_detected: false, onset_detected: false,
    estimated_tempo: 120, harmonicity: 0, spectral_rolloff: 0, zero_crossing_rate: 0, frequency_bands: { bass: 0, mid: 0, treble: 0 } };
}

// desktop_audio_features: AudioAnalyzer keys (including its adaptive beat), then the desktop's amplitude (RMS) and
// frequency (peak of |rfft| of the raw chunk). mode 'analyzer' keeps AudioAnalyzer's own amplitude (peak).
export function desktopFeatures(x, sampleRate, analyzer, now, mode = 'desktop') {
  const f = analyzer ? analyzer.analyze(x, now) : {};
  if (mode === 'analyzer' && analyzer) return { ...f, frequency: f.dominant_frequency, raw_data: x };
  let sq = 0; for (const v of x) sq += v * v;
  const amplitude = x.length ? Math.sqrt(sq / x.length) : 0;
  let frequency = 0;
  if (x.length) {
    const m = rfftAbs(x); let pi = 0;
    for (let k = 1; k < m.length; k++) if (m[k] > m[pi]) pi = k;
    frequency = pi * sampleRate / x.length;
  }
  return { ...f, amplitude, beat_detected: !!f.beat_detected, frequency, raw_data: x };
}
