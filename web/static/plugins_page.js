// #/plugins: every plugin from the Python catalogue (/api/plugins) with a still frame rendered by its JS port after
// four seconds of the simulated features (launcher.py), its parameters and defaults, and a link into the studio.
import { route, api, app, list, esc, onLeave } from './core.js';
import { ArtRunner } from './art_runner.js';
import { simulatedFeatures } from './audio_feed.js';
import { title } from './params_panel.js';

const fmt = v => (typeof v === 'number' && !Number.isInteger(v) ? +v.toFixed(3) : v);

route('plugins', async () => {
  const plugins = await api('/plugins');
  app().innerHTML = `
  <p class="kicker">${plugins.length} plugins</p><h1 class="glow">Plugins</h1>
  <p class="lead">Each plugin is a class in <code>plugins/</code> with <code>update(audio_features, dt)</code>,
  <code>render(surface)</code> and a dictionary of parameters. Frames below are drawn in your browser by the JavaScript
  ports after four seconds of the simulated audio features from <code>launcher.py</code>.</p>
  <div class="grid">${list(plugins, (p, i) => `
    <div class="card pcard">
      <canvas id="thumb-${i}" width="800" height="600" role="img" aria-label="Still frame of ${esc(p.name)}"></canvas>
      <b>${esc(p.name)}</b><span>${esc(p.description)}</span>
      ${p.doc && p.doc !== p.description ? `<small>${esc(p.doc)}</small>` : ''}
      <div class="params">${list(Object.entries(p.parameters), ([k, v]) => `${esc(title(k))} = ${esc(fmt(v))}`, ' · ')}</div>
      <span><a href="#/studio?plugin=${encodeURIComponent(p.name)}">Open in the studio</a> ·
        <a href="https://github.com/gddickinson/dynamic-art-generator/blob/main/${esc(p.source)}" target="_blank" rel="noopener">${esc(p.source)}</a></span>
    </div>`)}</div>`;
  let alive = true;
  onLeave(() => { alive = false; });
  let t = 0;
  const feed = { features: () => simulatedFeatures(t) };
  for (let i = 0; i < plugins.length && alive; i++) {
    await new Promise(r => setTimeout(r, 30));
    const canvas = document.getElementById(`thumb-${i}`);
    if (!canvas) break;
    const runner = new ArtRunner(canvas, feed);
    await runner.use(plugins[i].name);
    for (let k = 0; k < 240; k++) { t = k / 60; runner.step(); }
    runner.draw();
  }
});
