// node audio.test.mjs: the JS demo signal and audio feature extraction against tests/fixtures/audio_reference.json
// (written by scripts/make_fixtures.py from web/demo_signal.py and the real utils AudioAnalyzer / desktop features).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { demoSignal } from './demo_signal.js';
import { runReference } from './reference.js';

const ref = JSON.parse(readFileSync(new URL('../../tests/fixtures/audio_reference.json', import.meta.url)));
const close = (a, b, tol = 1e-9) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));

const full = demoSignal();
let maxd = 0;
ref.demo_head.forEach((v, i) => { maxd = Math.max(maxd, Math.abs(full[i] - v)); });
ref.demo_probe.index.forEach((ix, i) => { maxd = Math.max(maxd, Math.abs(full[ix] - ref.demo_probe.value[i])); });
assert.ok(maxd < 1e-9, `demo signal differs by ${maxd}`);
let abs = 0; for (const v of full) abs += Math.abs(v);
assert.ok(close(abs, ref.demo_abs_sum), `demo abs sum ${abs} vs ${ref.demo_abs_sum}`);
console.log(`ok   demo signal: ${full.length} samples, max diff ${maxd.toExponential(1)}`);

const js = runReference(ref.rows.length, full, ref);
let n = 0, worst = 0;
ref.rows.forEach((r, i) => {
  for (const [k, v] of Object.entries(r)) {
    const got = js[i][k];
    if (Array.isArray(v)) v.forEach((x, j) => { assert.ok(close(got[j], x), `chunk ${i} ${k}[${j}]: ${got[j]} vs ${x}`); n++; });
    else if (typeof v === 'boolean') { assert.equal(got, v, `chunk ${i} ${k}`); n++; }
    else { assert.ok(close(got, v), `chunk ${i} ${k}: ${got} vs ${v}`); worst = Math.max(worst, Math.abs(got - v) / Math.max(1, Math.abs(v))); n++; }
  }
});
console.log(`ok   features: ${ref.rows.length} chunks, ${n} values, max rel diff ${worst.toExponential(1)}`);
