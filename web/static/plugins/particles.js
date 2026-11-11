// Port of plugins/particles.py (ParticlePlugin): sand/smoke-like particles spawned around an audio-driven shape.
import { ArtPlugin, hsvToRgb, get, bands, int, pymod } from '../plugin_base.js';
import { uniform, choice } from '../pyrand.js';

export class Particle {
  constructor(x, y, vx, vy, life, color, size = 2.0) {
    Object.assign(this, { x, y, vx, vy, life, max_life: life, color, size, initial_size: size });
    this.mass = 1.0; this.drag = 0.98; this.bounce = 0.3;
    this.rotation = uniform(0, 2 * Math.PI); this.angular_velocity = uniform(-2, 2);
  }

  update(dt, forces, bounds) {
    this.vx += forces[0] * dt / this.mass; this.vy += forces[1] * dt / this.mass;
    this.vx *= this.drag; this.vy *= this.drag;
    this.x += this.vx * dt; this.y += this.vy * dt;
    this.rotation += this.angular_velocity * dt;
    if (this.x < 0) { this.x = 0; this.vx = Math.abs(this.vx) * this.bounce; }
    else if (this.x > bounds[0]) { this.x = bounds[0]; this.vx = -Math.abs(this.vx) * this.bounce; }
    if (this.y < 0) { this.y = 0; this.vy = Math.abs(this.vy) * this.bounce; }
    else if (this.y > bounds[1]) { this.y = bounds[1]; this.vy = -Math.abs(this.vy) * this.bounce; }
    this.life -= dt;
    // A zero lifetime (reachable from the particle_life slider) means the particle is already dead.
    const lr = this.max_life > 0 ? this.life / this.max_life : 0.0;
    this.size = this.initial_size * lr;
    const alpha = Math.max(0, Math.min(255, int(lr * 255)));
    this.color = [this.color[0], this.color[1], this.color[2], alpha];
  }

  is_alive() { return this.life > 0 && this.size > 0.1; }
}

export class ParticlePlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Particles';
  static PLUGIN_DESCRIPTION = 'Dynamic particle systems that respond to audio';
  static SOURCE = 'plugins/particles.py';

  constructor(size) {
    super(ParticlePlugin.PLUGIN_NAME, size);
    this.particles = []; this.max_particles = 1000; this.spawn_rate = 50; this.spawn_timer = 0;
    this.shape_type = 'circle'; this.shape_center = [size[0] / 2, size[1] / 2]; this.shape_size = 100;
    this.shape_rotation = 0; this.shape_velocity = [0, 0];
    this.particle_life = 3.0; this.particle_speed = 50; this.gravity = 20; this.wind = 0;
    this.turbulence = 10; this.attraction = 0;
    this.audio_sensitivity = 1.0; this.beat_burst_strength = 0; this.beat_decay = 0.9; this.frequency_influence = 1.0;
    this.color_hue = 0; this.color_saturation = 0.7; this.color_brightness = 0.9; this.color_cycle_speed = 30;
    this.particle_size_range = [1, 4]; this.show_shape_outline = true;
    this.particle_trails = false; this.collision_response = true; this.particle_interaction = false;
    this.parameters = {
      max_particles: this.max_particles, spawn_rate: this.spawn_rate, particle_life: this.particle_life,
      particle_speed: this.particle_speed, gravity: this.gravity, wind: this.wind, turbulence: this.turbulence,
      attraction: this.attraction, audio_sensitivity: this.audio_sensitivity, shape_size: this.shape_size,
      color_cycle_speed: this.color_cycle_speed, color_saturation: this.color_saturation,
      color_brightness: this.color_brightness, show_shape_outline: this.show_shape_outline,
    };
    this._last_beat_time = 0;
    this._shape_target = [...this.shape_center];
    this._emitter_points = [];
  }

  update(f, dt) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), t = this.now();
    if (beat && t - this._last_beat_time > 0.1) {
      this.beat_burst_strength = Math.min(this.beat_burst_strength + amplitude * 20, 10.0);
      this._last_beat_time = t;
    } else this.beat_burst_strength *= this.beat_decay;
    this.color_hue = pymod(this.color_hue + this.color_cycle_speed * dt, 360);
    if (frequency > 0) this.color_hue = pymod(this.color_hue + frequency * 0.01 * dt, 360);
    this._update_shape(f, dt);
    this._spawn_particles(f, dt);
    this._update_particles(f, dt);
    this.particles = this.particles.filter(p => p.is_alive());
  }

  _update_shape(f, dt) {
    const amplitude = get(f, 'amplitude', 0), frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    const current = this.shape_size + amplitude * 100 * this.audio_sensitivity;
    const bassMove = (fb.bass ?? 0) * 50, trebleMove = (fb.treble ?? 0) * 30;
    const cx = this.surface_size[0] / 2, cy = this.surface_size[1] / 2, t = this.now();
    const tx = cx + Math.sin(t * 2) * bassMove, ty = cy + Math.cos(t * 3) * trebleMove;
    this._shape_target[0] += (tx - this._shape_target[0]) * dt * 2;
    this._shape_target[1] += (ty - this._shape_target[1]) * dt * 2;
    this.shape_center = [...this._shape_target];
    this.shape_rotation += frequency * 0.001 * dt + amplitude * 50 * dt;
    this._update_emitter_points(current);
  }

  _update_emitter_points(size) {
    const pts = this._emitter_points = [], [cx, cy] = this.shape_center;
    if (this.shape_type === 'circle') {
      const n = Math.max(8, int(size / 10));
      for (let i = 0; i < n; i++) {
        const a = (2 * Math.PI * i / n) + this.shape_rotation;
        pts.push([cx + size * Math.cos(a), cy + size * Math.sin(a)]);
      }
    } else if (this.shape_type === 'square') {
      const h = size / 2, per = Math.max(2, int(size / 20));
      for (let side = 0; side < 4; side++) {
        for (let i = 0; i < per; i++) {
          const t = i / per;
          if (side === 0) pts.push([cx - h + t * size, cy - h]);
          else if (side === 1) pts.push([cx + h, cy - h + t * size]);
          else if (side === 2) pts.push([cx + h - t * size, cy + h]);
          else pts.push([cx - h, cy + h - t * size]);
        }
      }
    } else pts.push(this.shape_center);
  }

  _spawn_particles(f, dt) {
    if (this.particles.length >= this.max_particles) return;
    const amplitude = get(f, 'amplitude', 0);
    const rate = this.spawn_rate + amplitude * 100 * this.audio_sensitivity + this.beat_burst_strength * 5;
    this.spawn_timer += dt;
    const interval = 1.0 / Math.max(1, rate);
    let n = 0;
    while (this.spawn_timer >= interval && this.particles.length < this.max_particles) {
      n++; this.spawn_timer -= interval;
      if (n > 50) break;
    }
    for (let i = 0; i < n; i++) this._spawn_single_particle(f);
  }

  _spawn_single_particle(f) {
    const amplitude = get(f, 'amplitude', 0), fb = bands(f);
    let x, y;
    if (this._emitter_points.length) {
      const sp = choice(this._emitter_points);
      x = sp[0] + uniform(-10, 10); y = sp[1] + uniform(-10, 10);
    } else {
      x = this.shape_center[0] + uniform(-this.shape_size / 2, this.shape_size / 2);
      y = this.shape_center[1] + uniform(-this.shape_size / 2, this.shape_size / 2);
    }
    const speed = this.particle_speed * (1.0 + amplitude * this.audio_sensitivity);
    let angle = uniform(0, 2 * Math.PI);
    if ((fb.bass ?? 0) * 2 > 0.5) {
      angle = Math.atan2(y - this.shape_center[1], x - this.shape_center[0]) + uniform(-0.5, 0.5);
    }
    const vx = speed * Math.cos(angle);
    let vy = speed * Math.sin(angle);
    vy -= (fb.treble ?? 0) * 30;
    const life = this.particle_life * (1.0 + amplitude * 0.5) * uniform(0.5, 1.5);
    const hue = pymod(this.color_hue + uniform(-30, 30), 360);
    const sat = Math.max(0, Math.min(1, this.color_saturation + (fb.mid ?? 0) * 0.3));
    const color = hsvToRgb(hue, sat, this.color_brightness);
    const size = uniform(this.particle_size_range[0], this.particle_size_range[1]);
    this.particles.push(new Particle(x, y, vx, vy, life, color, size));
  }

  _update_particles(f, dt) {
    const amplitude = get(f, 'amplitude', 0), fb = bands(f);
    const bassForce = (fb.bass ?? 0) * 100, turb = this.turbulence * (1 + amplitude * 2);
    const beatForce = this.beat_burst_strength * 50, [cx, cy] = this.shape_center;
    for (const p of this.particles) {
      let fx = this.wind, fy = this.gravity;
      fx += uniform(-turb, turb); fy += uniform(-turb, turb);
      const dx = p.x - cx, dy = p.y - cy, d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0) {
        const nx = dx / d, ny = dy / d;
        if (bassForce > 0) { fx += nx * bassForce; fy += ny * bassForce; }
        if (beatForce > 0) { fx += nx * beatForce; fy += ny * beatForce; }
        if (this.attraction > 0) { const a = this.attraction * d * 0.01; fx -= nx * a; fy -= ny * a; }
      }
      p.update(dt, [fx, fy], this.surface_size);
    }
  }

  render(g) {
    if (this.show_shape_outline) this._draw_shape_outline(g);
    const b = g.blended();
    for (const p of this.particles) {
      const pos = [int(p.x), int(p.y)], size = Math.max(1, int(p.size));
      if (p.color.length === 4) b.circle(p.color, pos, size);   // SRCALPHA temp surface + blit
      else g.circle(p.color, pos, size);
    }
  }

  _draw_shape_outline(g) {
    const c = hsvToRgb(this.color_hue, 0.5, 0.5);
    const center = [int(this.shape_center[0]), int(this.shape_center[1])], size = int(this.shape_size);
    if (this.shape_type === 'circle') g.circle(c, center, size, 2);
    else if (this.shape_type === 'square') g.rect(c, [center[0] - size, center[1] - size, size * 2, size * 2], 2);
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'max_particles') {
      this.max_particles = Math.max(10, int(value));
      while (this.particles.length > this.max_particles) this.particles.shift();
    } else if (name === 'spawn_rate') {
      this.spawn_rate = Math.max(1, Number(value));
    } else if (name === 'shape_size') {
      this.shape_size = Math.max(10, Number(value));
      this._update_emitter_points(this.shape_size);
    } else if (name === 'color_saturation' || name === 'color_brightness') {
      this[name] = Math.max(0, Math.min(1, Number(value))); this.parameters[name] = this[name];
    }
  }

  reset() {
    this.particles = [];
    this.shape_center = [this.surface_size[0] / 2, this.surface_size[1] / 2];
    this._shape_target = [...this.shape_center];
    this.color_hue = 0; this.shape_rotation = 0; this.beat_burst_strength = 0; this.spawn_timer = 0;
    this._update_emitter_points(this.shape_size);
  }

  info() { return { particles: this.particles.length }; }
}
