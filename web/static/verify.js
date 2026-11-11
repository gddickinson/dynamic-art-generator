// #/verify: the JS ports against the Python code, live in the browser.
//  1. Audio features: the demo signal regenerated in JS, analysed chunk by chunk, compared with the Python run of
//     utils AudioAnalyzer + desktop_audio_features on the same signal (/api/audio_reference).
//  2. Plugins: each JS port's default parameters compared with the Python get_parameters() (/api/plugins).
import { route, api, app, list, esc } from './core.js';
import { demoSignal } from './demo_signal.js';
import { runReference, compare } from './reference.js';
import { pluginClass } from './plugins/index.js';
import { SIZE } from './art_runner.js';

const KEYS = ['amplitude', 'beat_detected', 'frequency', 'dominant_frequency', 'spectral_centroid', 'estimated_tempo', 'bands'];
const show = v => (Array.isArray(v) ? v.map(x => x.toFixed(3)).join(' / ') : typeof v === 'number' ? (+v.toPrecision(7)).toString() : String(v));

route('verify', async () => {
  app().innerHTML = '<p class="kicker">JavaScript vs Python</p><h1 class="glow">Verify</h1><p class="mute">Running…</p>';
  const [ref, plugins] = await Promise.all([api('/audio_reference'), api('/plugins')]);
  const t0 = performance.now();
  const js = runReference(ref.rows.length, demoSignal(ref.rows.length * ref.chunk), ref);
  const r = compare(ref.rows, js, 1e-9);
  const ms = performance.now() - t0;
  const s = ref.summary;
  const prow = [];
  for (const p of plugins) {
    const Cls = await pluginClass(p.name);
    const got = new Cls(SIZE).getParameters();
    const diff = Object.keys(p.parameters).filter(k => typeof got[k] === 'number'
      ? Math.abs(got[k] - p.parameters[k]) > 1e-9 * Math.max(1, Math.abs(p.parameters[k])) : got[k] !== p.parameters[k]);
    const extra = Object.keys(got).filter(k => !(k in p.parameters));
    prow.push([p.name, Object.keys(p.parameters).length, diff.concat(extra)]);
  }
  const rows = ref.rows.slice(40, 52);
  app().innerHTML = `
  <p class="kicker">JavaScript vs Python</p><h1 class="glow">Verify</h1>
  <p class="lead">The web app runs JavaScript ports of the repository's Python code. This page re-runs the checks that
  the node tests run in CI, here in your browser.</p>
  <h2>Audio features</h2>
  <p>The built-in demo signal (DrumMachine kick, snare and hi-hat at 120 BPM plus a tone gliding between 240 and 640 Hz)
  is regenerated in JS, cut into ${s.chunks} chunks of ${ref.chunk} samples (${s.seconds} s at ${ref.rate} Hz) and analysed
  by the JS port; the Python numbers come from <code>utils.audio_utils.AudioAnalyzer</code> and
  <code>utils.desktop_features</code> on the same signal.</p>
  <div class="tiles">
    <div class="tile"><b class="${r.bad.length ? 'err' : 'ok'}">${r.bad.length ? r.bad.length + ' differ' : 'match'}</b><span>${r.n} values compared</span></div>
    <div class="tile"><b>${r.worst.toExponential(1)}</b><span>largest relative difference</span></div>
    <div class="tile"><b>${s.analyzer_beats}</b><span>adaptive beats (AudioAnalyzer)</span></div>
    <div class="tile"><b>${s.desktop_beats}</b><span>desktop beats (RMS &gt; 0.1)</span></div>
    <div class="tile"><b>${ms.toFixed(0)} ms</b><span>JS analysis time</span></div>
  </div>
  ${r.bad.length ? `<pre class="err">${esc(r.bad.slice(0, 10).join('\n'))}</pre>` : ''}
  <p class="small mute">The desktop app counts a chunk as a beat whenever its RMS exceeds 0.1, so at full demo level every
  chunk is a “beat”; the studio's <em>Feature definitions</em> menu switches to AudioAnalyzer's adaptive beats.</p>
  <h3>Chunks 40–51: Python / JavaScript</h3>
  <div class="scroll"><table><tr><th>chunk</th>${list(KEYS, k => `<th>${k}</th>`)}</tr>
  ${list(rows, (row, i) => `<tr><td>${40 + i}</td>${list(KEYS, k => {
    const a = show(row[k]), b = show(js[40 + i][k]);
    return `<td class="mono">${a === b ? a : `${a}<br>${b}`}</td>`;
  })}</tr>`)}</table></div>
  <h2>Plugin parameters</h2>
  <p>Default parameters of each JS port against <code>get_parameters()</code> of the Python plugin (the node test also
  checks <code>set_parameter</code> behaviour and runs every plugin for 700 frames).</p>
  <div class="scroll"><table><tr><th>plugin</th><th>parameters</th><th>result</th></tr>
  ${list(prow, ([n, c, d]) => `<tr><td>${esc(n)}</td><td>${c}</td><td class="${d.length ? 'err' : 'ok'}">${d.length ? 'differs: ' + esc(d.join(', ')) : 'identical'}</td></tr>`)}
  </table></div>`;
});
