// Runs one plugin on a canvas like main.DynamicArtGenerator.update_loop: every 1/60 s the plugin gets the latest
// audio features and dt = 1/60, then the surface is filled black and the plugin renders onto it.
// Plugins read time.time() through a simulated clock that advances 1/60 s per update (so pausing really pauses).
import { Gfx } from './pg.js';
import { setClock } from './plugin_base.js';
import { pluginClass } from './plugins/index.js';
import { seed } from './pyrand.js';

export const SIZE = [800, 600];   // config.json application.canvas_size
const DT = 1 / 60;

export class ArtRunner {
  constructor(canvas, feed) {
    this.canvas = canvas; this.feed = feed;
    this.g = new Gfx(canvas.getContext('2d'), SIZE[0], SIZE[1], false);
    this.clock = 1000; this.acc = 0; this.last = null; this.plugin = null; this.paused = false;
    this.fps = 0; this.frames = 0; this.fpsT = performance.now(); this.features = {};
    setClock(() => this.clock);
  }

  async use(name, params = null) {
    const Cls = await pluginClass(name);
    seed((Date.now() % 2147483647) || 1);
    setClock(() => this.clock);
    this.plugin = new Cls(SIZE);
    if (params) for (const [k, v] of Object.entries(params)) this.plugin.setParameter(k, v);
    return this.plugin;
  }

  step() {
    this.features = this.feed.features();
    this.clock += DT;
    this.plugin.update(this.features, DT);
  }

  draw() {
    this.g.fill([0, 0, 0]);
    this.plugin.render(this.g);
  }

  // Call every animation frame with the rAF timestamp.
  tick(t) {
    if (!this.plugin) return;
    if (this.last === null) this.last = t;
    const el = Math.min(0.1, (t - this.last) / 1000); this.last = t;
    if (!this.paused) {
      this.acc += el;
      let n = 0;
      while (this.acc >= DT && n < 3) { this.step(); this.acc -= DT; n++; }
      if (n === 3) this.acc = 0;
      if (n) this.draw();
    }
    this.frames++;
    if (t - this.fpsT > 1000) { this.fps = this.frames * 1000 / (t - this.fpsT); this.frames = 0; this.fpsT = t; }
  }

  // Advance n updates at once (used for still frames under reduced motion).
  warm(n) { for (let i = 0; i < n; i++) this.step(); this.draw(); }

  snapshot(name = 'art') {
    return new Promise(res => this.canvas.toBlob(b => res([`${name.toLowerCase().replace(/[^a-z0-9]+/g, '_')}.png`, b]), 'image/png'));
  }
}
