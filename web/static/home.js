// Home page: hero with a live plugin driven (silently) by the built-in demo signal, counts from the API, entry cards.
import { route, api, app, list, animate, esc } from './core.js';
import { AudioFeed } from './audio_feed.js';
import { ArtRunner } from './art_runner.js';

const DOORS = [
  ['#/studio', 'Studio', 'The working app: choose any of the plugins or an example preset, feed it the demo signal, an audio file or your microphone, adjust its parameters and save snapshots.'],
  ['#/plugins', 'Plugins', 'Every visual plugin in the repository with its description, parameters and a still frame rendered in your browser.'],
  ['#/verify', 'Verify', 'The browser audio analysis against the Python code: the same demo signal, compared feature by feature, chunk by chunk.'],
  ['#/about', 'About', 'How sound becomes features and features become pictures, how to run the desktop and web apps, credits.'],
];
const HERO = ['Cosmic Web', 'Pendulum', 'Neural Flow', 'Rehoboam', 'Musical Flock'];

route('home', async () => {
  const [info, plugins] = await Promise.all([api('/info'), api('/plugins')]);
  app().innerHTML = `
  <section class="hero two">
    <div>
      <p class="kicker">Audio-reactive · plugin-based · real-time</p>
      <h1 class="glow">Dynamic Art Generator</h1>
      <p class="lead">${esc(info.summary)} This site runs it in your browser: JavaScript ports of all
      ${info.plugins} Python plugins, fed by a port of the repository's audio analysis.</p>
      <a class="btn" href="#/studio">Open the studio</a><a class="btn alt" href="#/plugins">See the plugins</a>
    </div>
    <figure class="fig"><canvas id="hero" width="800" height="600" role="img" aria-label="Live art plugin reacting to the built-in demo signal"></canvas>
      <figcaption class="small mute" id="hero-cap"></figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.plugins}</b><span>visual plugins</span></div>
    <div class="tile"><b>${info.parameters}</b><span>plugin parameters</span></div>
    <div class="tile"><b>${info.presets}</b><span>example presets</span></div>
    <div class="tile"><b>${(info.sample_rate / 1000).toFixed(1)} kHz</b><span>${info.chunk_size}-sample audio chunks</span></div>
    <div class="tile"><b>${info.canvas_size.join('×')}</b><span>canvas, ${info.target_fps} updates/s</span></div>
  </div>
  <div class="grid">${list(DOORS, ([href, t, d]) => `<a class="card door" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  <h2>The plugins</h2>
  <p>${list(plugins, (p, i) => `<a class="tag ${'abc'[i % 3]}" href="#/studio?plugin=${encodeURIComponent(p.name)}">${esc(p.name)}</a>`)}</p>`;
  hero();
});

async function hero() {
  const canvas = document.getElementById('hero'), cap = document.getElementById('hero-cap');
  const feed = new AudioFeed();
  const runner = new ArtRunner(canvas, feed);
  let i = 0;
  const show = async name => { await runner.use(name); cap.textContent = `${name}, default parameters, driven (silently) by the built-in demo signal.`; };
  await show(HERO[0]);
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { runner.warm(240); return; }
  let since = performance.now();
  animate(t => {
    runner.tick(t);
    if (t - since > 15000) { since = t; i = (i + 1) % HERO.length; show(HERO[i]); }
  });
}
