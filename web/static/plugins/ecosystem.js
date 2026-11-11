// Port of plugins/ecosystem.py (MusicalEcosystemPlugin): prey boids and predators living, breeding and hunting to music.
import { ArtPlugin, get, int } from '../plugin_base.js';
import { uniform, random } from '../pyrand.js';
import { hsvToRgbClamped, trianglePoints } from './vector2d.js';
import { PreyBoid, Predator } from './ecosystem_life.js';

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

export class MusicalEcosystemPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Musical Ecosystem';
  static PLUGIN_DESCRIPTION = 'Living predator-prey ecosystem dancing to music';
  static SOURCE = 'plugins/ecosystem.py';

  constructor(size) {
    super(MusicalEcosystemPlugin.PLUGIN_NAME, size);
    this.initial_boids = 40; this.max_boids = 150; this.num_predators = 2; this.max_predators = 5;
    this.boids = []; this.predators = []; this.total_births = 0; this.total_deaths = 0;
    this.show_trails = true; this.show_hunt_radius = false; this.trail_opacity = 0.7; this.background_fade = 0.02;
    // audio_sensitivity and predator_aggression_multiplier are parameters the Python plugin stores but never reads.
    this.audio_sensitivity = 1.0; this.reproduction_rate_multiplier = 1.0; this.predator_aggression_multiplier = 1.0;
    this.auto_spawn_predators = true; this.auto_spawn_boids = true; this.min_population = 10;
    this.parameters = {
      initial_boids: this.initial_boids, num_predators: this.num_predators, audio_sensitivity: this.audio_sensitivity,
      reproduction_rate_multiplier: this.reproduction_rate_multiplier,
      predator_aggression_multiplier: this.predator_aggression_multiplier, trail_opacity: this.trail_opacity,
      show_trails: this.show_trails, show_hunt_radius: this.show_hunt_radius,
      auto_spawn_predators: this.auto_spawn_predators, auto_spawn_boids: this.auto_spawn_boids,
    };
    this.create_initial_ecosystem();
    this.ecosystem_age = 0.0; this.last_status_update = 0;
  }

  create_initial_ecosystem() {
    const [W, H] = this.surface_size;
    this.boids = []; this.predators = [];
    for (let i = 0; i < int(this.initial_boids); i++) this.boids.push(new PreyBoid(uniform(50, W - 50), uniform(50, H - 50)));
    for (let i = 0; i < int(this.num_predators); i++) this.predators.push(new Predator(uniform(100, W - 100), uniform(100, H - 100)));
    this.total_births = 0; this.total_deaths = 0; this.ecosystem_age = 0.0;
  }

  update(f, dt) {
    this.ecosystem_age += dt;
    if (f && f.amplitude !== undefined) f = { ...f, amplitude: f.amplitude * this.audio_sensitivity };
    const newBoids = [], living = [];
    for (const b of this.boids) {
      if (b.is_alive) {
        newBoids.push(...b.update(dt, this.boids, this.predators, f, this.surface_size));
        living.push(b);
      } else this.total_deaths++;
    }
    if (newBoids.length > 0) {
      const factor = this.reproduction_rate_multiplier * get(f, 'amplitude', 0.5);
      for (const baby of newBoids) {
        if (random() < factor && living.length < this.max_boids) { living.push(baby); this.total_births++; }
      }
    }
    this.boids = living;
    const livingPred = [];
    for (const p of this.predators) {
      p.aggression = this.predator_aggression_multiplier;
      p.update(dt, this.boids, f, this.surface_size);
      if (p.energy > 0 || livingPred.length < 1) livingPred.push(p);
    }
    this.predators = livingPred;
    this.manage_ecosystem_balance(f);
  }

  manage_ecosystem_balance(f) {
    const [W, H] = this.surface_size;
    const prey = this.boids.filter(b => b.is_alive).length, preds = this.predators.length;
    if (this.auto_spawn_boids && prey < this.min_population) {
      for (let i = 0; i < this.min_population - prey; i++) {
        const nb = new PreyBoid(uniform(50, W - 50), uniform(50, H - 50));
        nb.age = uniform(0, 2);
        this.boids.push(nb);
      }
    }
    if (this.auto_spawn_predators) {
      let ideal = Math.max(1, Math.min(this.max_predators, Math.floor(prey / 20)));
      if (get(f, 'amplitude', 0) > 0.7 && random() < 0.01) ideal += 1;
      if (preds < ideal) this.predators.push(new Predator(uniform(100, W - 100), uniform(100, H - 100)));
    }
  }

  render(g) {
    if (this.show_trails) this.render_trails(g);
    if (this.show_hunt_radius) {
      for (const p of this.predators) g.circle([80, 0, 0], [int(p.location.x), int(p.location.y)], int(p.hunt_radius), 1);
    }
    for (const b of this.boids) {
      if (!b.is_alive) continue;
      const brightness = Math.min(1.0, 0.8 + Math.min(0.3, b.panic_level * 0.1) + b.birth_flash * 0.2);
      const color = hsvToRgbClamped(b.color_hue, 0.8, brightness);
      const size = Math.max(1, b.r * (1 + b.panic_level * 0.2 + b.birth_flash * 0.3));
      this.draw_triangle(g, int(b.location.x), int(b.location.y), b.velocity.heading(), size, color, b.birth_flash);
    }
    for (const p of this.predators) {
      const x = int(p.location.x), y = int(p.location.y);
      const ef = p.energy / p.max_energy, hf = Math.min(1.0, p.hunger * 0.3);
      const brightness = Math.min(1.0, 0.7 + ef * 0.3 + p.kill_flash * 0.2);
      const color = hsvToRgbClamped(p.color_hue + hf * 30, 0.9, brightness);
      const size = p.r * (1 + p.size_pulse * 0.2 + ef * 0.3);
      this.draw_triangle(g, x, y, p.velocity.heading(), size, color, p.kill_flash);
      this.draw_energy_bar(g, x, y - size - 8, ef);
    }
    this.render_ecosystem_info(g);
  }

  render_trails(g) {
    const b = g.blended();
    const dots = (owner, scale, s, v, r) => {
      const n = owner.trail.length;
      if (n < 2) return;
      for (let i = 1; i < n; i++) {
        const alpha = clamp(int((i / n) * this.trail_opacity * scale), 0, 255);
        if (alpha > 0) {
          const [x, y, hue] = owner.trail[i];
          b.circle([...hsvToRgbClamped(hue, s, v), alpha], [int(x), int(y)], r);
        }
      }
    };
    for (const boid of this.boids) if (boid.is_alive) dots(boid, 255, 0.6, 0.8, 1);
    for (const p of this.predators) dots(p, 200, 0.8, 0.9, 2);
  }

  draw_triangle(g, x, y, angle, size, color, glow) {
    if (size <= 0) return;
    if (glow > 0) {
      const gr = Math.max(1, int(size * 2 + glow * 4)), ga = clamp(int(glow * 80), 0, 255);
      if (ga > 0) g.blended().circle([...color, ga], [x, y], gr);
    }
    const pts = trianglePoints(x, y, angle, size);
    g.polygon(color, pts);
    g.polygon([255, 255, 255], pts, 1);
  }

  draw_energy_bar(g, x, y, ratio) {
    const bw = 20, bh = 3, left = x - Math.floor(bw / 2), top = int(y);
    g.rect([60, 60, 60], [left, top, bw, bh]);
    const fw = int(bw * ratio);
    if (fw > 0) g.rect(ratio > 0.6 ? [0, 255, 0] : ratio > 0.3 ? [255, 255, 0] : [255, 0, 0], [left, top, fw, bh]);
  }

  render_ecosystem_info(g) {
    const alive = this.boids.filter(b => b.is_alive);
    const avgAge = alive.length > 0 ? alive.reduce((s, b) => s + b.age, 0) / alive.length : 0;
    const energy = this.predators.reduce((s, p) => s + p.energy, 0);
    const kills = this.predators.reduce((s, p) => s + p.kills, 0);
    const stats = [`Prey: ${alive.length}`, `Predators: ${this.predators.length}`, `Births: ${this.total_births}`,
      `Deaths: ${this.total_deaths}`, `Avg Age: ${avgAge.toFixed(1)}`, `Predator Energy: ${energy.toFixed(0)}`,
      `Total Kills: ${kills}`];
    stats.forEach((s, i) => g.text(s, this.surface_size[0] - 150, 10 + i * 22, 20, [255, 255, 255]));
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'num_predators') {
      const target = Math.max(1, Math.min(5, int(value))), cur = this.predators.length;
      const [W, H] = this.surface_size;
      if (target > cur) {
        for (let i = 0; i < target - cur; i++) this.predators.push(new Predator(uniform(100, W - 100), uniform(100, H - 100)));
      } else if (target < cur) this.predators = this.predators.slice(0, target);
      this.num_predators = target; this.parameters[name] = target;
    }
  }

  reset() { this.create_initial_ecosystem(); }

  info() {
    return { prey: this.boids.filter(b => b.is_alive).length, predators: this.predators.length,
      births: this.total_births, deaths: this.total_deaths };
  }
}
