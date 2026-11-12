// #/studio: the working app. Pick a plugin (or an example preset), drive it with the demo signal, an audio file, the
// microphone or the simulated features, tweak its parameters, and save PNG snapshots.
import { route, api, app, esc, animate, download, list, onLeave } from './core.js';
import { AudioFeed } from './audio_feed.js';
import { ArtRunner, SIZE } from './art_runner.js';
import { buildParams, syncParams } from './params_panel.js';
import { drawMeters } from './meters.js';

route('studio', async (_args, query) => {
  const [plugins, presets] = await Promise.all([api('/plugins'), api('/presets')]);
  const start = plugins.find(p => p.name === query.plugin) || plugins[0];
  app().innerHTML = `
  <div class="vis-head"><div><p class="kicker">Plugin studio</p><h1 class="glow" id="ptitle"></h1>
    <p class="small mute" id="pdesc"></p></div><p class="small mute" id="status" aria-live="polite"></p></div>
  <div class="srcbar">
    <div class="seg" role="group" aria-label="Audio source">
      <button id="src-demo" aria-pressed="true" class="on">Demo signal</button>
      <button id="src-file" aria-pressed="false">Audio file…</button>
      <button id="src-mic" aria-pressed="false">Microphone</button>
      <button id="src-sim" aria-pressed="false">Simulated</button>
    </div>
    <input type="file" id="file" accept="audio/*" hidden aria-label="Choose an audio file">
    <button class="alt" id="sound" aria-pressed="false">Sound on</button>
    <button class="alt" id="pause" aria-pressed="false">Pause</button>
    <button class="alt" id="reset">Reset</button>
    <button class="alt" id="snap">Snapshot PNG</button>
    <button class="alt" id="full">Fullscreen</button>
  </div>
  <div class="studio">
    <div>
      <div class="stage art" id="stage"><canvas id="art" width="${SIZE[0]}" height="${SIZE[1]}" role="img"
        aria-label="Generated art reacting to the audio"></canvas></div>
      <canvas id="meters" class="meters" width="800" height="70" role="img" aria-label="Audio features: amplitude, beat, dominant frequency and bands"></canvas>
      <p class="small mute">Keys: <b>Space</b> pause, <b>R</b> reset plugin, <b>N</b> next plugin, <b>S</b> snapshot, <b>F</b> fullscreen.</p>
    </div>
    <aside class="panel side-panel">
      <label for="plugin">Art plugin</label>
      <select id="plugin">${list(plugins, p => `<option ${p === start ? 'selected' : ''}>${esc(p.name)}</option>`)}</select>
      <label for="preset">Example preset <span class="mute">(example_presets.json)</span></label>
      <select id="preset"><option value="">—</option>${list(presets.presets, (p, i) => `<option value="${i}">${esc(p.name)} · ${esc(p.plugin)}</option>`)}</select>
      <div class="ctl" id="level-ctl"><label for="level">Demo level <b id="level-v">0.50</b></label>
        <input type="range" id="level" min="0.05" max="1" step="0.01" value="0.5"></div>
      <label for="mode">Feature definitions</label>
      <select id="mode"><option value="desktop">Desktop app: RMS amplitude</option>
        <option value="analyzer">AudioAnalyzer: peak amplitude</option></select>
      <h3>Plugin parameters</h3>
      <div id="params"></div>
      <p class="small mute" id="pinfo"></p>
    </aside>
  </div>`;

  const $ = id => document.getElementById(id);
  const feed = new AudioFeed();
  const runner = new ArtRunner($('art'), feed);
  let defaults = null;

  async function choose(name, params = null) {
    const meta = plugins.find(p => p.name === name);
    $('plugin').value = name;
    await runner.use(name, params);
    defaults = meta.parameters;
    $('ptitle').textContent = name;
    $('pdesc').innerHTML = `${esc(meta.description)} · <a href="https://github.com/gddickinson/dynamic-art-generator/blob/main/${esc(meta.source)}" target="_blank" rel="noopener">${esc(meta.source)}</a>`;
    buildParams($('params'), runner.plugin, defaults, (k, v) => { runner.plugin.setParameter(k, v); syncParams($('params'), runner.plugin); });
    history.replaceState(null, '', `#/studio?plugin=${encodeURIComponent(name)}`);
  }

  const setStatus = (extra = '') => {
    const what = { mic: 'listening to the microphone', file: `playing ${esc(feed.label)}${feed.ended ? ' (ended)' : ''}`,
      sim: 'simulated features (launcher.py)', demo: `demo signal${feed.sound ? ' with sound' : ' (silent)'}` }[feed.kind];
    $('status').innerHTML = `Source: ${what}${runner.paused ? ' · paused' : ''}. ${extra || feed.rateNote()}`;
    $('sound').textContent = feed.sound ? 'Sound off' : 'Sound on';
    $('sound').setAttribute('aria-pressed', feed.sound);
    $('sound').disabled = feed.kind === 'mic' || feed.kind === 'sim';
    $('level-ctl').hidden = feed.kind !== 'demo';
    for (const k of ['demo', 'file', 'mic', 'sim']) {
      $(`src-${k}`).classList.toggle('on', feed.kind === k); $(`src-${k}`).setAttribute('aria-pressed', feed.kind === k);
    }
  };
  const fail = e => setStatus(`<span class="err">${esc(e.message || e)}</span>`);
  const pause = p => { runner.paused = p; feed.setPaused(p); $('pause').textContent = p ? 'Resume' : 'Pause'; $('pause').setAttribute('aria-pressed', p); setStatus(); };

  $('src-demo').onclick = () => { feed.useDemo(); setStatus(); };
  $('src-sim').onclick = () => { feed.useSim(); setStatus(); };
  $('src-file').onclick = () => $('file').click();
  $('file').onchange = async ev => {
    const f = ev.target.files[0];
    if (!f) return;
    setStatus('Decoding…');
    try { await feed.useFile(f); setStatus(); } catch (e) { fail(new Error(`Could not decode ${f.name}: ${e.message}`)); }
  };
  $('src-mic').onclick = async () => {
    try { await feed.useMic(); setStatus(); } catch (e) { fail(new Error(`Microphone not available: ${e.message}`)); }
  };
  $('sound').onclick = () => { if (feed.sound) feed.mute(); else feed.play(); setStatus(); };
  $('pause').onclick = () => pause(!runner.paused);
  $('reset').onclick = () => { runner.plugin.reset(); syncParams($('params'), runner.plugin); };
  $('snap').onclick = async () => { const [n, b] = await runner.snapshot(runner.plugin.name); download(n, b); };
  $('full').onclick = () => { const s = $('stage'); document.fullscreenElement ? document.exitFullscreen() : s.requestFullscreen?.(); };
  $('level').oninput = e => { feed.setLevel(+e.target.value); $('level-v').textContent = (+e.target.value).toFixed(2); };
  $('mode').onchange = e => { feed.mode = e.target.value; };
  $('plugin').onchange = e => { $('preset').value = ''; choose(e.target.value); };
  $('preset').onchange = async e => {
    if (e.target.value === '') return;
    const p = presets.presets[+e.target.value];
    const known = plugins.find(x => x.name === p.plugin).parameters;
    const params = Object.fromEntries(Object.entries(p.parameters).filter(([k]) => k in known));
    await choose(p.plugin, params);
    const skipped = Object.keys(p.parameters).filter(k => !(k in known));
    setStatus(`Preset “${esc(p.name)}”: ${esc(p.description)}${skipped.length ? ` (not a parameter of the plugin, ignored: ${esc(skipped.join(', '))})` : ''}`);
  };
  const keys = e => {
    if (e.target.closest('input, select, textarea')) return;
    const k = e.key.toLowerCase();
    if (k === ' ') { e.preventDefault(); pause(!runner.paused); }
    else if (k === 'r') $('reset').click();
    else if (k === 's') $('snap').click();
    else if (k === 'f') $('full').click();
    else if (k === 'n') { const i = plugins.findIndex(p => p.name === runner.plugin.name); choose(plugins[(i + 1) % plugins.length].name); }
  };
  document.addEventListener('keydown', keys);

  await choose(start.name);
  setStatus();
  const meters = $('meters');
  let n = 0;
  const stop = animate(t => {
    runner.tick(t);
    if (n++ % 2 === 0) {
      drawMeters(meters, runner.features);
      const info = Object.entries(runner.plugin.info()).map(([k, v]) => `${k}: ${v}`).join(' · ');
      $('pinfo').textContent = `${info}${info ? ' · ' : ''}${runner.fps.toFixed(0)} fps`;
    }
    if (feed.kind === 'file' && feed.ended && !$('status').dataset.ended) { $('status').dataset.ended = 1; setStatus(); }
  });
  // core.onLeave keeps one stop function: stop the loop, the audio and the key handler together.
  onLeave(() => { stop(); feed.stopNodes(); document.removeEventListener('keydown', keys); });
});
