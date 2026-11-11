// Port of plugins/particle_fountain.py (ParticleFountainPlugin): thousands of particles from an audio-driven emitter.
import { ArtPlugin, hsvToRgb, get, int, pymod } from '../plugin_base.js';
import { uniform } from '../pyrand.js';
import { FountainParticle, glowStack } from './particle_fountain_parts.js';

export class ParticleFountainPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Particle Fountain';
  static PLUGIN_DESCRIPTION = 'High-performance fountain of thousands of particles';
  static SOURCE = 'plugins/particle_fountain.py';

  constructor(size) {
    super(ParticleFountainPlugin.PLUGIN_NAME, size);
    this.particles = []; this.num_particles = 5000; this.max_particles = 10000;
    this.emitter_x = size[0] / 2; this.emitter_y = size[1] / 2;
    this.emitter_target_x = this.emitter_x; this.emitter_target_y = this.emitter_y; this.emitter_smoothing = 0.1;
    this.gravity_strength = 1.0; this.wind_force = 0.0; this.turbulence = 0.1;
    this.audio_sensitivity = 1.0; this.bass_lift = 1.0; this.treble_spread = 1.0; this.frequency_color_influence = 1.0;
    this.particle_size_range = [2, 8]; this.color_mode = 'rainbow'; this.base_hue = 200;
    this.fade_trails = true; this.glow_effect = true;
    this.use_batch_rendering = true; this.render_quality = 'high';
    this.parameters = {
      num_particles: this.num_particles, audio_sensitivity: this.audio_sensitivity,
      gravity_strength: this.gravity_strength, wind_force: this.wind_force, turbulence: this.turbulence,
      bass_lift: this.bass_lift, treble_spread: this.treble_spread, base_hue: this.base_hue,
      glow_effect: this.glow_effect, fade_trails: this.fade_trails,
    };
    this.create_particles();
    this.frame_count = 0; this.last_fps_time = this.now(); this.current_fps = 60;
  }

  create_particles() {
    this.particles = [];
    for (let i = 0; i < int(this.num_particles); i++) {
      const p = new FountainParticle(this.emitter_x, this.emitter_y);
      p.gravity.y = 0.15 * this.gravity_strength; p.gravity.x = 0.15 * this.wind_force;   // keep the settings
      p.lifespan = uniform(0, 255);
      this.particles.push(p);
    }
  }

  update_emitter_position(f) {
    const frequency = get(f, 'dominant_frequency', 0);
    const fb = get(f, 'frequency_bands', { bass: 0, mid: 0, treble: 0 });
    const cx = this.surface_size[0] / 2, cy = this.surface_size[1] / 2, t = this.now();
    const range = 150 * this.audio_sensitivity;
    const bassX = (fb.bass ?? 0) * range * Math.sin(t * 2);
    const midY = (fb.mid ?? 0) * range * 0.5 * Math.cos(t * 1.5);
    const ti = (fb.treble ?? 0) * 50;
    const trX = ti * Math.cos(t * 4), trY = ti * Math.sin(t * 4);
    const fi = frequency > 0 ? frequency / 1000.0 : 0;
    const fX = fi * 100 * Math.sin(t * 3);
    this.emitter_target_x = cx + bassX + trX + fX;
    this.emitter_target_y = cy + midY + trY;
    const m = 50;
    this.emitter_target_x = Math.max(m, Math.min(this.surface_size[0] - m, this.emitter_target_x));
    this.emitter_target_y = Math.max(m, Math.min(this.surface_size[1] - m, this.emitter_target_y));
    this.emitter_x += (this.emitter_target_x - this.emitter_x) * this.emitter_smoothing;
    this.emitter_y += (this.emitter_target_y - this.emitter_y) * this.emitter_smoothing;
  }

  update(f, _dt) {
    this.update_emitter_position(f);
    const fb = get(f, 'frequency_bands', {});
    const scaled = {
      amplitude: get(f, 'amplitude', 0) * this.audio_sensitivity,
      beat_detected: get(f, 'beat_detected', false),
      dominant_frequency: get(f, 'dominant_frequency', 0),
      frequency_bands: { bass: (fb.bass ?? 0) * this.bass_lift, mid: fb.mid ?? 0, treble: (fb.treble ?? 0) * this.treble_spread },
    };
    for (const p of this.particles) {
      if (p.is_dead()) p.rebirth(this.emitter_x, this.emitter_y);
      else p.update(scaled);
    }
    this.frame_count++;
    const t = this.now();
    if (t - this.last_fps_time > 1.0) { this.current_fps = this.frame_count; this.frame_count = 0; this.last_fps_time = t; }
  }

  render(g) {
    if (this.use_batch_rendering) this.render_batched(g); else this.render_individual(g);
    this.render_emitter(g);
  }

  render_batched(g) {
    const groups = { high: [], medium: [], low: [] }, [W, H] = this.surface_size;
    for (const p of this.particles) {
      if (p.is_dead()) continue;
      const alpha = p.get_alpha(), pos = [int(p.position.x), int(p.position.y)], size = Math.max(1, int(p.size));
      if (pos[0] < -size || pos[0] > W + size || pos[1] < -size || pos[1] > H + size) continue;
      const item = [pos, size, this.calculate_particle_color(p), alpha];
      (alpha > 200 ? groups.high : alpha > 100 ? groups.medium : groups.low).push(item);
    }
    for (const q of ['high', 'medium', 'low']) if (groups[q].length) this.render_particle_group(g, groups[q], q);
  }

  render_particle_group(g, items, quality) {
    if (quality === 'high' && this.glow_effect) {
      for (const [pos, size, color, alpha] of items) this.render_particle_with_glow(g, pos, size, color, alpha);
    } else if (quality === 'medium') {
      const b = g.blended();
      for (const [pos, size, color, alpha] of items) b.circle([...color, alpha], pos, size);
    } else {
      // Opaque circles: batch consecutive same-colour discs into one path (identical pixels, fewer fills).
      const ctx = g.ctx;
      let cur = null;
      for (const [pos, size, color] of items) {
        const css = g.col(color);
        if (css !== cur) { if (cur) ctx.fill(); ctx.fillStyle = css; ctx.beginPath(); cur = css; }
        ctx.moveTo(pos[0] + size, pos[1]); ctx.arc(pos[0], pos[1], size, 0, Math.PI * 2);
      }
      if (cur) ctx.fill();
    }
  }

  render_particle_with_glow(g, pos, size, color, alpha) {
    const gs = size * 3, rings = [];
    for (let r = gs; r > 0; r -= 2) {
      const ga = int((alpha / 255) * (r / gs) * 50);
      if (ga > 0) rings.push([r, ga]);
    }
    glowStack(g.blended(), color, pos, rings, size, alpha);
  }

  render_individual(g) {
    for (const p of this.particles) {
      if (p.is_dead()) continue;
      const pos = [int(p.position.x), int(p.position.y)], size = Math.max(1, int(p.size)), alpha = p.get_alpha();
      if (alpha > 0) {
        const color = this.calculate_particle_color(p);
        if (this.glow_effect) this.render_particle_with_glow(g, pos, size, color, alpha);
        else g.circle(color, pos, size);
      }
    }
  }

  render_emitter(g) {
    const pos = [int(this.emitter_x), int(this.emitter_y)];
    const pulse = 0.5 + 0.5 * Math.sin(this.now() * 5), radius = int(8 + pulse * 5);
    const col = hsvToRgb(this.base_hue, 1.0, 1.0), rings = [];
    for (let r = radius * 2; r > 0; r -= 2) rings.push([r, int(100 * (r / (radius * 2)))]);
    glowStack(g.blended(), col, pos, rings.filter(([, a]) => a > 0));
  }

  calculate_particle_color(p) {
    if (this.color_mode === 'mono') return hsvToRgb(this.base_hue, p.saturation, p.brightness);
    if (this.color_mode === 'frequency') return hsvToRgb(pymod(this.base_hue + p.position.y * 0.5, 360), p.saturation, p.brightness);
    return hsvToRgb(p.hue, p.saturation, p.brightness);
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'num_particles') {
      const n = Math.max(100, Math.min(this.max_particles, int(value)));
      if (n !== this.particles.length) { this.num_particles = n; this.create_particles(); this.parameters[name] = n; }
    } else if (name === 'base_hue') {
      this.base_hue = pymod(Number(value), 360); this.parameters[name] = this.base_hue;
    } else if (name === 'gravity_strength') {
      for (const p of this.particles) p.gravity.y = 0.15 * this.gravity_strength;
    } else if (name === 'wind_force') {   // sideways acceleration on the gravity_strength scale
      for (const p of this.particles) p.gravity.x = 0.15 * this.wind_force;
    }
  }

  reset() {
    this.emitter_x = this.surface_size[0] / 2; this.emitter_y = this.surface_size[1] / 2;
    this.emitter_target_x = this.emitter_x; this.emitter_target_y = this.emitter_y;
    this.create_particles();
  }

  info() { return { particles: this.particles.length, alive: this.particles.filter(p => !p.is_dead()).length }; }
}
