// Port of web/demo_signal.py: the built-in demo loop (DrumMachine kick/snare/hi-hat at 120 BPM + a gliding tone).
// Same formulas and the same mulberry32 noise as the Python, so audio.test.mjs can compare samples.
export const RATE = 44100, BPM = 120, LOOP_SECONDS = 16;
const GAIN = { kick: 0.6, snare: 0.3, hihat: 0.12, tone: 0.2 };

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export { mulberry32 };

function gaussOf(rnd) {
  let u = 0;
  while (u === 0) u = rnd();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rnd());
}

// np.linspace(0, d, int(RATE * d))
function linspace(d) {
  const n = Math.trunc(RATE * d), t = new Float64Array(n);
  for (let i = 0; i < n; i++) t[i] = n === 1 ? 0 : d * i / (n - 1);
  return t;
}

// DrumMachine._generate_kick / _snare / _hihat with mulberry32 Gaussian noise.
export function drumSounds(seed = 1) {
  const rnd = mulberry32(seed);
  let t = linspace(0.2);
  const kick = t.map(v => Math.exp(-v * 8) * Math.sin(2 * Math.PI * (60 * Math.exp(-v * 30)) * v));
  for (let i = 0; i < t.length; i++) kick[i] += 0.1 * gaussOf(rnd) * Math.exp(-t[i] * 8) * 0.3;
  t = linspace(0.15);
  const snare = new Float64Array(t.length);
  for (let i = 0; i < t.length; i++) snare[i] = 0.3 * Math.sin(2 * Math.PI * 200 * t[i]) + gaussOf(rnd) * 0.7;
  for (let i = 0; i < t.length; i++) snare[i] *= Math.exp(-t[i] * 15);
  t = linspace(0.1);
  const hihat = new Float64Array(t.length);
  for (let i = 0; i < t.length; i++) hihat[i] = gaussOf(rnd) * Math.exp(-t[i] * 40) * 0.5;
  return { kick, snare, hihat };
}

// n samples of the demo loop (default: one full loop) as Float64Array.
export function demoSignal(n = Math.trunc(LOOP_SECONDS * RATE), seed = 1) {
  const out = new Float64Array(n), w = 2 * Math.PI / LOOP_SECONDS;
  for (let k = 0; k < n; k++) {
    const t = k / RATE;
    out[k] = GAIN.tone * Math.sin(2 * Math.PI * (440 * t + 200 / w * (1 - Math.cos(w * t))));
  }
  const sounds = drumSounds(seed), eighth = Math.round(RATE * 30 / BPM);
  for (let i = 0, start = 0; start < n; i++, start += eighth) {
    const beatInBar = Math.floor(i / 2) % 4, hits = ['hihat'];
    if (i % 2 === 0) hits.push(beatInBar === 0 || beatInBar === 2 ? 'kick' : 'snare');
    for (const name of hits) {
      const s = sounds[name], len = Math.min(s.length, n - start);
      for (let j = 0; j < len; j++) out[start + j] += GAIN[name] * s[j];
    }
  }
  return out;
}
