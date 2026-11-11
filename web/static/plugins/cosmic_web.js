// Port of plugins/cosmic_web.py (CosmicWebPlugin): gravitational orbs joined by glowing connections, with trails,
// ripples, emitted particles and twinkling background stars.
import { ArtPlugin, hsvToRgb, get, bands, int, pymod } from '../plugin_base.js';
import { uniform } from '../pyrand.js';
import { CosmicOrb } from './cosmic_orb.js';

export class CosmicWebPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Cosmic Web';
  static PLUGIN_DESCRIPTION = 'Gravitational orbs forming a living cosmic network';
  static SOURCE = 'plugins/cosmic_web.py';

  constructor(size) {
    super(CosmicWebPlugin.PLUGIN_NAME, size);
    this.orbs = []; this.num_orbs = 8; this.orb_mass_range = [0.5, 2.0];
    this.background_stars = []; this.star_count = 100; this.connection_opacity = 0.7; this.trail_fade = 0.3;
    this.base_hue = 240; this.hue_shift_speed = 20; this.color_variance = 60;
    this.audio_sensitivity = 1.0; this.beat_amplification = 3.0; this.frequency_color_influence = 1.0;
    this.enable_trails = true; this.enable_particles = true; this.enable_connections = true;
    this.enable_ripples = true; this.enable_stars = true;
    this.gravity_strength = 1.0; this.expansion_force = 0.5; this.swirl_force = 0.3;
    this.parameters = {
      num_orbs: this.num_orbs, audio_sensitivity: this.audio_sensitivity,
      beat_amplification: this.beat_amplification, gravity_strength: this.gravity_strength,
      expansion_force: this.expansion_force, swirl_force: this.swirl_force,
      connection_opacity: this.connection_opacity, hue_shift_speed: this.hue_shift_speed,
      color_variance: this.color_variance, enable_trails: this.enable_trails,
      enable_particles: this.enable_particles, enable_connections: this.enable_connections,
      enable_stars: this.enable_stars,
    };
    this.create_orbs();
    this.create_background_stars();
    this.time_offset = 0;
  }

  create_orbs() {
    this.orbs = [];
    const [W, H] = this.surface_size;
    for (let i = 0; i < int(this.num_orbs); i++) {
      const cr = Math.min(W, H) * 0.3;
      const a = (2 * Math.PI * i / this.num_orbs) + uniform(-0.5, 0.5);
      const d = uniform(0.3, 1.0) * cr;
      const mass = uniform(this.orb_mass_range[0], this.orb_mass_range[1]);
      this.orbs.push(new CosmicOrb(W / 2 + d * Math.cos(a), H / 2 + d * Math.sin(a), mass));
    }
  }

  create_background_stars() {
    this.background_stars = [];
    for (let i = 0; i < this.star_count; i++) {
      this.background_stars.push({ x: uniform(0, this.surface_size[0]), y: uniform(0, this.surface_size[1]),
        brightness: uniform(0.1, 1.0), twinkle_phase: uniform(0, 2 * Math.PI), twinkle_speed: uniform(1, 3) });
    }
  }

  update(f, dt) {
    this.time_offset += dt;
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    this.base_hue = pymod(this.base_hue + this.hue_shift_speed * dt, 360);
    if (frequency > 0) this.base_hue = pymod(this.base_hue + frequency * 0.01 * this.frequency_color_influence * dt, 360);
    const t = this.now();
    for (const orb of this.orbs) {
      const scaled = {
        amplitude: amplitude * this.audio_sensitivity, beat_detected: beat, dominant_frequency: frequency,
        frequency_bands: { bass: (fb.bass ?? 0) * this.expansion_force, mid: fb.mid ?? 0, treble: (fb.treble ?? 0) * this.swirl_force },
      };
      orb.gravity_scale = this.gravity_strength;
      orb.update(dt, this.orbs, scaled, this.surface_size, t);
    }
    if (this.enable_stars) for (const s of this.background_stars) s.twinkle_phase += s.twinkle_speed * dt;
  }

  render(g) {
    if (this.enable_stars) this.render_background_stars(g);
    if (this.enable_connections) this.render_connections(g);
    if (this.enable_trails) this.render_trails(g);
    this.render_orbs(g);
    if (this.enable_particles) this.render_particles(g);
  }

  render_background_stars(g) {
    for (const s of this.background_stars) {
      const v = int(s.brightness * (0.5 + 0.5 * Math.sin(s.twinkle_phase)) * 255);
      g.circle([v, v, Math.min(255, int(v * 1.2))], [int(s.x), int(s.y)], 1);
    }
  }

  render_connections(g) {
    const b = g.blended();
    for (const orb1 of this.orbs) {
      for (const [orb2, strength] of orb1.get_connections()) {
        if (!this.orbs.includes(orb2)) continue;
        const color = hsvToRgb((orb1.color_shift + orb2.color_shift) / 2, 0.8, 0.9);
        const alpha = Math.max(0, Math.min(255, int(strength * this.connection_opacity * 255)));
        const s = [int(orb1.x), int(orb1.y)], e = [int(orb2.x), int(orb2.y)];
        // Python draws the glow lines on a temporary alpha surface placed over the pair (same pixels as direct).
        for (const th of [5, 3, 1]) b.line([...color, Math.max(0, Math.min(255, Math.floor(alpha / (th + 1))))], s, e, th);
      }
    }
  }

  render_trails(g) {
    const b = g.blended();
    for (const orb of this.orbs) {
      const n = orb.trail.length;
      if (n < 2) continue;
      for (let i = 1; i < n; i++) {
        const alpha = Math.max(0, Math.min(255, int((i / n) * this.trail_fade * 255)));
        const c = hsvToRgb(pymod(orb.color_shift + i * 10, 360), 0.6, 0.7);
        if (alpha > 0) b.circle([...c, alpha], [int(orb.trail[i][0]), int(orb.trail[i][1])], 3);
      }
    }
  }

  render_orbs(g) {
    const b = g.blended();
    for (const orb of this.orbs) {
      const hue = pymod(this.base_hue + orb.color_shift, 360);
      const oc = hsvToRgb(hue, 0.8, 0.9);
      const pos = [int(orb.x), int(orb.y)], radius = int(orb.radius);
      const gr = radius + 10, gc = hsvToRgb(hue, 0.6, 0.5);
      if (gr > 0) {
        // Python draws shrinking circles onto one SRCALPHA surface (each overwrites the pixels inside it), so each
        // 2-px annulus keeps its own alpha: drawn here as rings, the innermost as a disc.
        for (let r = gr; r > 0; r -= 2) {
          const a = Math.max(0, Math.min(255, int(100 * (r / gr) * 0.3)));
          if (a > 0) b.circle([...gc, a], pos, r, r > 2 ? 2 : 0);
        }
      }
      g.circle(oc, pos, radius);
      g.circle(hsvToRgb(hue, 1.0, 1.0), pos, Math.max(2, Math.floor(radius / 3)));
      if (this.enable_ripples) {
        for (const rp of orb.ripples) {
          const pr = rp.time / rp.max_time, rr = radius + pr * 30;
          const ra = int((1 - pr) * rp.intensity * 255);
          if (ra > 0 && rr > 0) b.circle([...oc, Math.max(0, Math.min(255, ra))], pos, int(rr), 2);
        }
      }
    }
  }

  render_particles(g) {
    const b = g.blended();
    for (const orb of this.orbs) {
      for (const p of orb.particles) {
        const alpha = Math.max(0, Math.min(255, int((p.life / p.max_life) * 255)));
        const c = hsvToRgb(pymod(p.color + this.time_offset * 50, 360), 0.9, 1.0);
        if (alpha > 0) b.circle([...c, alpha], [int(p.x), int(p.y)], 2);
      }
    }
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'num_orbs') {
      const n = Math.max(2, Math.min(20, int(value)));
      if (n !== this.orbs.length) { this.num_orbs = n; this.create_orbs(); this.parameters[name] = n; }
    } else if (name === 'connection_opacity' || name === 'trail_fade') {
      this[name] = Math.max(0, Math.min(1, Number(value))); this.parameters[name] = this[name];
    } else if (name === 'color_variance') {
      this.color_variance = Math.max(0, Math.min(180, Number(value))); this.parameters[name] = this.color_variance;
    }
  }

  reset() {
    this.create_orbs();
    this.base_hue = 240; this.time_offset = 0;
    for (const orb of this.orbs) {
      orb.energy = 0; orb.ripples = []; orb.particles = []; orb.trail = []; orb.connections.clear();
    }
  }

  info() {
    return { orbs: this.orbs.length, particles: this.orbs.reduce((s, o) => s + o.particles.length, 0) };
  }
}
