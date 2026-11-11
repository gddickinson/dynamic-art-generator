// Port of SmokeParticle and AIMonolith from plugins/digital_spectre.py.
import { get, bands, int, clamp, now } from '../plugin_base.js';
import { uniform, randint, random } from '../pyrand.js';

export class SmokeParticle {
  constructor(x, y, vx, vy, life, size = 2.0) {
    this.x = x; this.y = y; this.vx = vx; this.vy = vy;
    this.life = life; this.max_life = life; this.size = size; this.initial_size = size;
    this.rotation = uniform(0, 2 * Math.PI); this.angular_velocity = uniform(-2, 2);
    this.data_charge = uniform(0, 1); this.neural_connection = null;
  }

  update(dt, forces, bounds) {
    this.vx += forces[0] * dt; this.vy += forces[1] * dt;
    const t = now();
    this.vx += Math.sin(this.y * 0.01 + t * 2) * 20 * dt;
    this.vy += Math.cos(this.x * 0.01 + t * 1.5) * 15 * dt;
    const dx = this.x - bounds[0] / 2, dy = this.y - bounds[1] / 2;
    const d = Math.sqrt(dx * dx + dy * dy);
    if (d > 0) {
      const s = 30 / (1 + d * 0.01);
      this.vx += -dy / d * s * dt; this.vy += dx / d * s * dt;
    }
    this.vx *= 0.99; this.vy *= 0.99;
    this.x += this.vx * dt; this.y += this.vy * dt;
    this.rotation += this.angular_velocity * dt;
    this.life -= dt;
    const lp = 1 - this.life / this.max_life;
    const sf = lp < 0.3 ? lp / 0.3 : 1 - (lp - 0.3) / 0.7;
    this.size = this.initial_size * sf * 2;
    if (this.x < -50) this.x = bounds[0] + 50;
    else if (this.x > bounds[0] + 50) this.x = -50;
    if (this.y > bounds[1] + 50) this.y = -50;
  }

  is_alive() { return this.life > 0 && this.size > 0.1; }

  get_alpha() { return clamp(int(this.life / this.max_life * 180), 0, 255); }
}

export class AIMonolith {
  constructor(x, y, type = 'cube') {
    this.x = x; this.y = y; this.base_y = y; this.height = 0;
    this.max_height = uniform(80, 200); this.width = uniform(20, 60); this.depth = uniform(20, 60);
    this.type = type; this.emergence_phase = 0; this.pulse_energy = 0;
    this.data_flow_rate = uniform(0.5, 2.0); this.neural_activity = 0;
    this.scanning_phase = uniform(0, 2 * Math.PI); this.glitch_probability = 0.02;
    this.smoke_emitters = [];
    this.create_emitters();
    this.opacity = 0; this.edge_glow = 0; this.scan_lines = [];
  }

  create_emitters() {
    const n = randint(3, 8);
    for (let i = 0; i < n; i++) {
      const angle = 2 * Math.PI * i / n + uniform(-0.3, 0.3), dist = this.width * 0.7;
      this.smoke_emitters.push({
        x: this.x + dist * Math.cos(angle), y: this.y, angle,
        intensity: uniform(0.5, 1.0), timer: uniform(0, 1),
      });
    }
  }

  update(dt, f) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    const target = (fb.bass ?? 0) * 1.5 + amplitude * 0.5;
    if (target > this.emergence_phase) this.emergence_phase += 2.0 * dt;
    else this.emergence_phase -= 2.0 * dt * 0.5;
    this.emergence_phase = Math.max(0, Math.min(1, this.emergence_phase));
    this.height = this.max_height * this.emergence_phase;
    this.y = this.base_y - this.height;
    if (beat) this.pulse_energy = Math.min(this.pulse_energy + amplitude * 3, 2.0);
    else this.pulse_energy *= 0.95;
    this.neural_activity = (fb.mid ?? 0) * 2;
    this.scanning_phase += frequency * 0.001 * dt + dt * 3;
    this.glitch_probability = (fb.treble ?? 0) > 0.7 ? 0.1 : 0.02;
    this.opacity = Math.min(255, int(this.emergence_phase * 200 + this.pulse_energy * 55));
    this.edge_glow = this.neural_activity * 100 + this.pulse_energy * 50;
    for (const e of this.smoke_emitters) { e.timer += dt; e.y = this.y + uniform(-10, 10); }
  }

  should_emit_smoke(e) {
    const rate = this.data_flow_rate * (0.5 + this.emergence_phase * 0.5);
    return e.timer > 1.0 / rate;
  }

  emit_smoke(e) {
    e.timer = 0;
    const speed = uniform(10, 30) * (1 + this.neural_activity);
    const angle = e.angle + uniform(-0.5, 0.5);
    const vx = speed * Math.cos(angle) + uniform(-5, 5), vy = speed * Math.sin(angle) - 20;
    const life = uniform(3, 6) * (1 + this.emergence_phase);
    const size = uniform(1, 3) * (1 + this.pulse_energy * 0.3);
    return new SmokeParticle(e.x, e.y, vx, vy, life, size);
  }

  get_vertices() {
    if (this.height <= 0) return [];
    const hw = this.width / 2, hd = this.depth / 2;
    let go = 0;
    if (random() < this.glitch_probability) go = uniform(-5, 5);
    const x = this.x + go, y = this.y;
    if (this.type === 'pyramid') {
      return [[int(x), int(y)], [int(x - hw), int(y + this.height)], [int(x + hw), int(y + this.height)]];
    }
    if (this.type === 'neural_node') {
      const v = [];
      for (let i = 0; i < 6; i++) {
        const a = i * Math.PI / 3;
        v.push([int(x + hw * Math.cos(a)), int(y + this.height / 2 + hd * Math.sin(a))]);
      }
      return v;
    }
    // 'cube' (the only other type the plugin creates)
    return [[int(x - hw), int(y)], [int(x + hw), int(y)], [int(x + hw), int(y + this.height)], [int(x - hw), int(y + this.height)]];
  }
}
