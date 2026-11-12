// Port of CosmicOrb from plugins/cosmic_web.py: a fluid, gravitationally influenced orb with ripples, a trail and
// emitted particles. `connections` is keyed by the other orb object (Python: id(other)).
import { get, bands, pymod } from '../plugin_base.js';
import { uniform } from '../pyrand.js';

export class CosmicOrb {
  constructor(x, y, mass = 1.0) {
    this.x = x; this.y = y;
    this.vx = uniform(-20, 20); this.vy = uniform(-20, 20);
    this.mass = mass;
    this.gravity_scale = 1.0;   // the plugin's gravity_strength
    this.beat_scale = 1.0;      // the plugin's beat_amplification / its default 3.0
    this.base_radius = 10 + mass * 5; this.radius = this.base_radius;
    this.energy = 0.0;
    this.pulse_phase = uniform(0, 2 * Math.PI);
    this.color_shift = uniform(0, 360);
    this.fluidity = 0.3; this.surface_tension = 0.1; this.ripples = [];
    this.trail = []; this.max_trail_length = 20;
    this.connections = new Map();
    this.particle_timer = 0; this.particles = [];
  }

  update(dt, others, f, bounds, now) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    this.energy += amplitude * 10 * dt;
    this.energy *= 0.95;
    if (beat) { this.energy += amplitude * 20 * this.beat_scale; this.create_ripple(); }
    let fx = 0, fy = 0;
    for (const o of others) {
      if (o === this) continue;
      const dx = o.x - this.x, dy = o.y - this.y, d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0) {
        const m = (this.mass * o.mass) / (d * d + 100) * (0.5 * this.gravity_scale);
        fx += m * (dx / d); fy += m * (dy / d);
        const strength = Math.min(1.0, 200 / d);
        if (strength > 0.1) this.connections.set(o, strength);
      }
    }
    const bass = (fb.bass ?? 0) * 50;
    if (bass > 0) {
      const dx = this.x - bounds[0] / 2, dy = this.y - bounds[1] / 2, d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0) { fx += bass * (dx / d); fy += bass * (dy / d); }
    }
    const treble = (fb.treble ?? 0) * 30;
    if (treble > 0) {
      fx += treble * Math.sin(now * frequency * 0.01);
      fy += treble * Math.cos(now * frequency * 0.01);
    }
    this.vx += fx * dt; this.vy += fy * dt;
    this.vx *= 0.98; this.vy *= 0.98;
    this.x += this.vx * dt; this.y += this.vy * dt;
    const m = this.radius;
    if (this.x < m || this.x > bounds[0] - m) {
      this.vx *= -0.8; this.x = Math.max(m, Math.min(bounds[0] - m, this.x)); this.create_ripple();
    }
    if (this.y < m || this.y > bounds[1] - m) {
      this.vy *= -0.8; this.y = Math.max(m, Math.min(bounds[1] - m, this.y)); this.create_ripple();
    }
    const pulse = 1 + 0.3 * Math.sin(this.pulse_phase + now * 3);
    this.radius = this.base_radius * pulse * (1 + this.energy * 0.1) * (1 + amplitude * 0.5);
    this.color_shift += frequency * 0.001 * dt + amplitude * 50 * dt;
    this.color_shift = pymod(this.color_shift, 360);
    this.trail.push([this.x, this.y]);
    if (this.trail.length > this.max_trail_length) this.trail.shift();
    this.update_ripples(dt);
    if (this.energy > 5) {
      this.particle_timer += dt;
      if (this.particle_timer > 0.1) { this.emit_particle(); this.particle_timer = 0; }
    }
    this.update_particles(dt);
  }

  create_ripple() { this.ripples.push({ time: 0, max_time: 1.0, intensity: this.energy * 0.1 }); }

  update_ripples(dt) {
    for (const r of this.ripples) r.time += dt;
    this.ripples = this.ripples.filter(r => r.time <= r.max_time);
  }

  emit_particle() {
    const a = uniform(0, 2 * Math.PI), s = uniform(20, 50);
    this.particles.push({ x: this.x + Math.cos(a) * this.radius, y: this.y + Math.sin(a) * this.radius,
      vx: Math.cos(a) * s, vy: Math.sin(a) * s, life: uniform(1, 3), max_life: 3, color: this.color_shift });
  }

  update_particles(dt) {
    for (const p of this.particles) {
      p.x += p.vx * dt; p.y += p.vy * dt; p.life -= dt;
      p.vx *= 0.98; p.vy *= 0.98;
    }
    this.particles = this.particles.filter(p => p.life > 0);
  }

  get_connections() { return new Map(this.connections); }
}
