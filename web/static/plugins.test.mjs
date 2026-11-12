// Node test of the JavaScript plugin ports against the Python plugins (tests/fixtures/plugin_cases.json):
//   * name, description and default parameters equal the Python get_parameters();
//   * set_parameter(name, v) leaves the same get_parameters() as Python (for 2x, 0.37x and 0 of each default);
//   * 700 frames of simulated audio (the launcher/macos_demo features) + silence + empty features + reset run without
//     exceptions, and every drawing call receives finite numbers.
// Run: node web/static/plugins.test.mjs [--only "Plugin Name"]
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { mockGfx, allMocks } from './mock_canvas.mjs';
import { setClock } from './plugin_base.js';
import { seed } from './pyrand.js';
import { REGISTRY, pluginClass } from './plugins/index.js';

const fx = JSON.parse(readFileSync(new URL('../../tests/fixtures/plugin_cases.json', import.meta.url)));
const i = process.argv.indexOf('--only');
const only = i > 0 ? process.argv[i + 1] : null;
const SIZE = [800, 600];

let t = 1000;
setClock(() => t);

const close = (a, b, path) => {
  if (typeof b === 'number' && typeof a === 'number') {
    assert.ok(Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b)), `${path}: JS ${a} vs Python ${b}`);
  } else assert.deepEqual(a, b, path);
};

function simulated(time) {   // macos_demo.py / launcher.py fake_audio
  return {
    amplitude: 0.5 + 0.3 * Math.sin(time * 2), beat_detected: (time % 1.2) < 0.1,
    dominant_frequency: 440 + 200 * Math.sin(time * 0.5),
    frequency_bands: { bass: 0.3 + 0.2 * Math.sin(time), mid: 0.4 + 0.3 * Math.sin(time * 1.5), treble: 0.2 + 0.1 * Math.sin(time * 2) },
  };
}
const SILENT = { amplitude: 0, beat_detected: false, dominant_frequency: 0, frequency_bands: { bass: 0, mid: 0, treble: 0 } };

let n = 0;
for (const [name] of REGISTRY) {
  if (only && name !== only) continue;
  const py = fx.catalog.find(c => c.name === name);
  assert.ok(py, `${name} missing from fixture`);
  const Cls = await pluginClass(name);
  seed(7);
  const p = new Cls(SIZE);
  assert.equal(p.name, name);
  assert.equal(Cls.PLUGIN_DESCRIPTION, py.description, `${name} description`);
  const params = p.getParameters();
  assert.deepEqual(Object.keys(params), Object.keys(py.parameters), `${name} parameter names/order`);
  for (const k of Object.keys(py.parameters)) close(params[k], py.parameters[k], `${name}.${k} default`);
  for (const c of fx.set_cases.filter(c => c.plugin === name)) {
    const q = new Cls(SIZE);
    q.setParameter(c.param, c.value);
    const got = q.getParameters(), want = { ...py.parameters, ...c.after };
    for (const k of Object.keys(want)) close(got[k], want[k], `${name} after set ${c.param}=${c.value}: ${k}`);
  }
  const g = mockGfx(...SIZE);
  const frames = name === 'Noise Sphere' || name === 'Particle Fountain' ? 240 : 700;
  for (let f = 0; f < frames; f++) {
    t += 1 / 60;
    p.update(f < frames - 100 ? simulated(f / 60) : SILENT, 1 / 60);
    if (f % 7 === 0) { g.fill([0, 0, 0]); p.render(g); }
  }
  p.update({}, 1 / 60); p.render(g);
  p.reset(); p.update(simulated(1), 1 / 60); p.render(g);
  for (const k of Object.keys(params)) {           // every parameter at 2x and 0, then a few frames
    const v = params[k];
    for (const val of typeof v === 'boolean' ? [!v] : [v * 2, 0]) {
      const q = new Cls(SIZE); q.setParameter(k, val);
      for (let f = 0; f < 3; f++) { t += 1 / 60; q.update(simulated(f), 1 / 60); q.render(g); }
    }
  }
  const bad = allMocks().flatMap(m => m.bad);
  assert.deepEqual(bad.slice(0, 5), [], `${name}: non-finite drawing arguments`);
  assert.ok(g.ctx.calls > 100, `${name}: drew almost nothing (${g.ctx.calls} calls)`);
  n++;
  console.log(`ok ${name}: ${Object.keys(params).length} parameters, ${fx.set_cases.filter(c => c.plugin === name).length} set cases, ${g.ctx.calls} draw calls`);
}
assert.ok(n > 0, 'no plugin tested');
console.log(`plugins.test: ${n} plugin ports ok`);

// Musical Ecosystem prey hue = age hue + audio shift (tests/test_ecosystem_prey_hue.py checks the same numbers).
if (!only || only === 'Musical Ecosystem') {
  const { PreyBoid } = await import('./plugins/ecosystem_life.js');
  const b = new PreyBoid(100, 100); b.age = 5; b.max_age = 20;
  b.update_audio_response({ amplitude: 1.0, dominant_frequency: 1000 });
  assert.ok(Math.abs(b.color_hue - 87) < 1e-9, `prey hue ${b.color_hue}`);
  console.log('ok Musical Ecosystem prey hue follows the audio');
}
