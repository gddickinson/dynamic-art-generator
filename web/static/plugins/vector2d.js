// Port of the Vector2D class that plugins/musical_flock.py and plugins/ecosystem.py each define (identical code).
export class Vector2D {
  constructor(x = 0, y = 0) { this.x = Number(x); this.y = Number(y); }
  add(o) { this.x += o.x; this.y += o.y; }
  sub(o) { this.x -= o.x; this.y -= o.y; }
  mult(s) { this.x *= s; this.y *= s; }
  div(s) { if (s !== 0) { this.x /= s; this.y /= s; } }
  mag() { return Math.sqrt(this.x * this.x + this.y * this.y); }
  normalize() { const m = this.mag(); if (m > 0) this.div(m); }
  limit(max) { if (this.mag() > max) { this.normalize(); this.mult(max); } }
  heading() { return Math.atan2(this.y, this.x); }
  copy() { return new Vector2D(this.x, this.y); }
  static dist(a, b) { const dx = b.x - a.x, dy = b.y - a.y; return Math.sqrt(dx * dx + dy * dy); }
  static sub_static(a, b) { return new Vector2D(a.x - b.x, a.y - b.y); }
}

// The clamping hsv_to_rgb both plugins define (s and v clamped to 0..1, output clamped to 0..255).
export function hsvToRgbClamped(h, s, v) {
  h = ((h % 360) + 360) % 360;
  s = Math.max(0, Math.min(1, s)); v = Math.max(0, Math.min(1, v));
  const c = v * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = v - c;
  let r, g, b;
  if (h < 60) [r, g, b] = [c, x, 0];
  else if (h < 120) [r, g, b] = [x, c, 0];
  else if (h < 180) [r, g, b] = [0, c, x];
  else if (h < 240) [r, g, b] = [0, x, c];
  else if (h < 300) [r, g, b] = [x, 0, c];
  else [r, g, b] = [c, 0, x];
  const q = u => Math.max(0, Math.min(255, Math.trunc((u + m) * 255)));
  return [q(r), q(g), q(b)];
}

// The boid triangle both plugins draw: front at 2*size, back corners at +-2.8 rad, truncated to ints.
export function trianglePoints(x, y, angle, size) {
  const t = Math.trunc;
  return [
    [t(x + Math.cos(angle) * size * 2), t(y + Math.sin(angle) * size * 2)],
    [t(x + Math.cos(angle + 2.8) * size), t(y + Math.sin(angle + 2.8) * size)],
    [t(x + Math.cos(angle - 2.8) * size), t(y + Math.sin(angle - 2.8) * size)],
  ];
}
