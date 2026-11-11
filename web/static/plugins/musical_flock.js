// Port of plugins/musical_flock.py (MusicalFlockPlugin): Reynolds boids whose flocking weights follow the audio bands.
import { ArtPlugin, get, int, pymod } from '../plugin_base.js';
import { uniform, randint } from '../pyrand.js';
import { Vector2D, hsvToRgbClamped, trianglePoints } from './vector2d.js';
import { FlockBoid } from './flock_boid.js';

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

export class MusicalFlockPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Musical Flock';
  static PLUGIN_DESCRIPTION = 'Flocking boids that dance to music';
  static SOURCE = 'plugins/musical_flock.py';

  constructor(size) {
    super(MusicalFlockPlugin.PLUGIN_NAME, size);
    this.boids = []; this.num_boids = 60; this.max_boids = 200;
    this.show_trails = true; this.show_boid_bodies = true; this.trail_opacity = 0.6; this.boid_size_multiplier = 1.0;
    this.base_hue = 200; this.hue_spread = 60; this.color_cycle_speed = 30;
    this.audio_sensitivity = 1.0; this.beat_spawn_threshold = 0.7; this.frequency_color_influence = 1.0;
    // Stored and shown as parameters, but (as in the Python plugin) the boids use their own fixed radii and speed.
    this.neighbor_radius = 50; this.separation_radius = 25; this.max_speed = 2.5; this.max_force = 0.05;
    this.enable_beat_spawning = true; this.enable_audio_forces = true; this.enable_color_cycling = true;
    this.parameters = {
      num_boids: this.num_boids, audio_sensitivity: this.audio_sensitivity, neighbor_radius: this.neighbor_radius,
      separation_radius: this.separation_radius, max_speed: this.max_speed, trail_opacity: this.trail_opacity,
      boid_size_multiplier: this.boid_size_multiplier, color_cycle_speed: this.color_cycle_speed,
      hue_spread: this.hue_spread, show_trails: this.show_trails, enable_beat_spawning: this.enable_beat_spawning,
      enable_audio_forces: this.enable_audio_forces,
    };
    this.create_initial_flock();
    this.time_offset = 0; this.last_beat_spawn = 0;
  }

  create_initial_flock() {
    this.boids = [];
    const cx = this.surface_size[0] / 2, cy = this.surface_size[1] / 2;
    for (let i = 0; i < int(this.num_boids); i++) {
      let x = cx + uniform(-50, 50), y = cy + uniform(-50, 50);
      x = clamp(x, 50, this.surface_size[0] - 50); y = clamp(y, 50, this.surface_size[1] - 50);
      const b = new FlockBoid(x, y);
      b.color_hue = pymod(this.base_hue + uniform(-this.hue_spread / 2, this.hue_spread / 2), 360);
      this.boids.push(b);
    }
  }

  update(f, dt) {
    this.time_offset += dt;
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0);
    if (this.enable_color_cycling) this.base_hue = pymod(this.base_hue + this.color_cycle_speed * dt, 360);
    if (this.enable_beat_spawning && beat && amplitude > this.beat_spawn_threshold
        && this.boids.length < this.max_boids && this.now() - this.last_beat_spawn > 0.5) {
      this.spawn_boid_at_random_location();
      this.last_beat_spawn = this.now();
    }
    const scaled = {
      amplitude: amplitude * this.audio_sensitivity, beat_detected: beat,
      dominant_frequency: frequency * this.frequency_color_influence,
      frequency_bands: get(f, 'frequency_bands', { bass: 0, mid: 0, treble: 0 }),
    };
    for (const b of this.boids) {
      b.base_maxspeed = this.max_speed; b.neighbor_dist = this.neighbor_radius; b.desired_separation = this.separation_radius;
      b.run(this.boids, scaled, this.surface_size);
    }
  }

  spawn_boid_at_random_location() {
    const [W, H] = this.surface_size, edge = randint(0, 3);
    let x, y;
    if (edge === 0) { x = uniform(0, W); y = 0; }
    else if (edge === 1) { x = W; y = uniform(0, H); }
    else if (edge === 2) { x = uniform(0, W); y = H; }
    else { x = 0; y = uniform(0, H); }
    const b = new FlockBoid(x, y);
    b.color_hue = pymod(this.base_hue + uniform(-this.hue_spread / 2, this.hue_spread / 2), 360);
    const angle = Math.atan2(H / 2 - y, W / 2 - x), speed = uniform(1, 3);
    b.velocity = new Vector2D(Math.cos(angle) * speed, Math.sin(angle) * speed);
    this.boids.push(b);
  }

  render(g) {
    if (this.show_trails) this.render_trails(g);
    if (this.show_boid_bodies) this.render_boids(g);
  }

  render_trails(g) {
    const b = g.blended();
    for (const boid of this.boids) {
      const n = boid.trail.length;
      if (n < 2) continue;
      for (let i = 1; i < n; i++) {
        const alpha = clamp(int((i / n) * this.trail_opacity * 255), 0, 255);
        if (alpha > 0) {
          const [x, y, hue] = boid.trail[i];
          // Python: circle r=2 on a 6x6 SRCALPHA surface blitted at (int(x)-3, int(y)-3).
          b.circle([...hsvToRgbClamped(hue, 0.7, 0.8), alpha], [int(x), int(y)], 2);
        }
      }
    }
  }

  render_boids(g) {
    for (const boid of this.boids) {
      const x = int(boid.location.x), y = int(boid.location.y);
      const brightness = Math.min(1.0, 0.9 + Math.min(0.3, boid.energy * 0.1));
      const saturation = Math.min(1.0, 0.8 + boid.beat_response * 0.2);
      const color = hsvToRgbClamped(boid.color_hue, saturation, brightness);
      const size = Math.max(1, boid.r * this.boid_size_multiplier * (1 + boid.beat_response * 0.3));
      this.draw_boid_triangle(g, x, y, boid.velocity.heading(), size, color, boid.beat_response);
    }
  }

  draw_boid_triangle(g, x, y, angle, size, color, glow) {
    if (size <= 0) return;
    const pts = trianglePoints(x, y, angle, size);
    if (glow > 0) {
      const gr = Math.max(1, int(size * 2 + glow * 5)), ga = clamp(int(glow * 50), 0, 255);
      if (ga > 0 && gr > 0) g.blended().circle([...color, ga], [x, y], gr);
    }
    g.polygon(color, pts);
    g.polygon([255, 255, 255], pts, 1);
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'num_boids') {
      const target = Math.max(5, Math.min(200, int(value))), cur = this.boids.length;
      if (target > cur) {
        for (let i = 0; i < target - cur; i++) {
          const b = new FlockBoid(uniform(50, this.surface_size[0] - 50), uniform(50, this.surface_size[1] - 50));
          b.color_hue = this.base_hue + uniform(-this.hue_spread / 2, this.hue_spread / 2);
          this.boids.push(b);
        }
      } else if (target < cur) this.boids = this.boids.slice(0, target);
      this.num_boids = target; this.parameters[name] = target;
    } else if (name === 'trail_opacity' || name === 'boid_size_multiplier') {
      this[name] = Math.max(0.1, Math.min(2.0, Number(value))); this.parameters[name] = this[name];
    } else if (name === 'hue_spread') {
      this.hue_spread = Math.max(0, Math.min(180, Number(value))); this.parameters[name] = this.hue_spread;
    }
  }

  reset() {
    this.create_initial_flock();
    this.base_hue = 200; this.time_offset = 0; this.last_beat_spawn = 0;
  }

  info() { return { boids: this.boids.length }; }
}
