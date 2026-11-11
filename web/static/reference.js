// Replays the Python reference run (web/audio_reference.py) in JS: the demo signal cut into chunks, analysed by the
// AudioAnalyzer port with the stream clock. Used by audio.test.mjs and the Verify page.
import { AudioAnalyzer, desktopFeatures } from './audio_analyzer.js';

export function runReference(rows, signal, { chunk, rate, t0 }) {
  const a = new AudioAnalyzer(rate, chunk), b = new AudioAnalyzer(rate, chunk), out = [];
  for (let i = 0; i < rows; i++) {
    const x = signal.subarray(i * chunk, (i + 1) * chunk), now = t0 + i * chunk / rate;
    const f = desktopFeatures(x, rate, a, now), raw = b.analyze(x, now);
    out.push({ ...f, bands: [f.frequency_bands.bass, f.frequency_bands.mid, f.frequency_bands.treble],
      analyzer_amplitude: raw.amplitude, analyzer_beat: raw.beat_detected });
  }
  return out;
}


// Compare JS rows to the Python rows; returns {n, worst, bad[]} (relative tolerance tol).
export function compare(pyRows, jsRows, tol = 1e-9) {
  let n = 0, worst = 0; const bad = [];
  const close = (a, b) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));
  pyRows.forEach((r, i) => {
    for (const [k, v] of Object.entries(r)) {
      const got = jsRows[i][k];
      const vals = Array.isArray(v) ? v.map((x, j) => [x, got[j], `${k}[${j}]`]) : [[v, got, k]];
      for (const [want, have, name] of vals) {
        n++;
        if (typeof want === 'boolean') { if (want !== have) bad.push(`chunk ${i} ${name}: ${have} vs ${want}`); continue; }
        worst = Math.max(worst, Math.abs(have - want) / Math.max(1, Math.abs(want)));
        if (!close(have, want)) bad.push(`chunk ${i} ${name}: ${have} vs ${want}`);
      }
    }
  });
  return { n, worst, bad };
}
