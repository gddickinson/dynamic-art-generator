// Helpers for particle_fountain.js: Vector2D and FountainParticle from plugins/particle_fountain.py, and the
// "concentric circles drawn onto one SRCALPHA surface" glow, which pygame composes by REPLACING pixels (each smaller
// circle overwrites the larger one), so it is drawn here as annuli, each with its own alpha.
import { uniform } from '../pyrand.js';
import { pymod, int } from '../plugin_base.js';

export class Vector2D {
  constructor(x = 0, y = 0) { this.x = +x; this.y = +y; }
  add(o) { if (o instanceof Vector2D) { this.x += o.x; this.y += o.y; } else { this.x += o; this.y += o; } }
  mult(s) { this.x *= s; this.y *= s; }
  copy() { return new Vector2D(this.x, this.y); }
  magnitude() { return Math.sqrt(this.x * this.x + this.y * this.y); }
  normalize() { const m = this.magnitude(); if (m > 0) { this.x /= m; this.y /= m; } }
  limit(max) { if (this.magnitude() > max) { this.normalize(); this.mult(max); } }
  static random() { const a = uniform(0, 2 * Math.PI); return new Vector2D(Math.cos(a), Math.sin(a)); }
  static from_angle(a, m = 1) { return new Vector2D(Math.cos(a) * m, Math.sin(a) * m); }
}

export class FountainParticle {
  constructor(ex, ey) {
    this.position = new Vector2D(ex, ey);
    this.velocity = new Vector2D();
    this.acceleration = new Vector2D();
    this.gravity = new Vector2D(0, 0.15);
    this.lifespan = 255.0; this.max_lifespan = 255.0;
    this.size = uniform(2, 8); this.initial_size = this.size;
    this.hue = uniform(0, 360); this.saturation = uniform(0.6, 1.0); this.brightness = uniform(0.7, 1.0);
    this.rebirth(ex, ey);
  }

  rebirth(x, y) {
    this.position.x = x + uniform(-10, 10);
    this.position.y = y + uniform(-5, 5);
    const angle = uniform(-Math.PI * 0.3, -Math.PI * 0.7), speed = uniform(1, 6);
    this.velocity = Vector2D.from_angle(angle, speed);
    this.velocity.x += uniform(-2, 2);
    this.lifespan = this.max_lifespan;
    this.size = this.initial_size;
    this.hue = uniform(0, 360);
  }

  update(f) {
    const amplitude = f.amplitude ?? 0, frequency = f.dominant_frequency ?? 0, fb = f.frequency_bands;
    this.acceleration = this.gravity.copy();
    this.acceleration.y -= (fb.bass ?? 0) * 0.3;
    const tf = (fb.treble ?? 0) * 2.0 * (f.turbulence ?? 0.1);   // turbulence parameter, default 0.1
    this.acceleration.x += uniform(-tf, tf);
    this.hue += (fb.mid ?? 0) * 100;
    this.velocity.add(this.acceleration);
    this.velocity.limit(12);
    this.position.add(this.velocity);
    this.lifespan -= 1.5 + amplitude * 2;
    const lr = this.lifespan / this.max_lifespan;
    this.size = this.initial_size * (0.5 + 0.5 * lr);
    this.hue += frequency * 0.01;
    this.hue = pymod(this.hue, 360);
  }

  is_dead() { return this.lifespan <= 0; }
  get_alpha() { return Math.max(0, Math.min(255, int((this.lifespan / this.max_lifespan) * 255))); }
}

// Draw circles (radius r, alpha a) listed largest first, as pygame leaves them on one SRCALPHA surface: a pixel
// takes the alpha of the smallest circle covering it. `rings` = [[r, a], ...]; then the core disc (coreR, coreA)
// if coreR > 0. b is a blended Gfx; the result is composited once, like the blit.
export function glowStack(b, rgb, center, rings, coreR = 0, coreA = 0) {
  const ctx = b.ctx, [cx, cy] = center;
  for (let i = 0; i < rings.length; i++) {
    const [r, a] = rings[i];
    const inner = Math.max(i + 1 < rings.length ? rings[i + 1][0] : 0, coreR);
    if (r <= inner) continue;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    if (inner > 0) ctx.arc(cx, cy, inner, 0, Math.PI * 2, true);
    ctx.fillStyle = `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${a / 255})`;
    ctx.fill();
  }
  if (coreR > 0) b.circle([...rgb, coreA], center, coreR);
}
