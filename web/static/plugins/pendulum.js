// Port of plugins/pendulum.py (PendulumPlugin): an elliptical pendulum leaving a fading rainbow trail.
import { ArtPlugin, hsvToRgb, get, bands, int, pymod } from '../plugin_base.js';
import { uniform } from '../pyrand.js';

export class PendulumPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Pendulum';
  static PLUGIN_DESCRIPTION = 'Elliptical pendulum trails that respond to audio';
  static SOURCE = 'plugins/pendulum.py';

  constructor(size) {
    super(PendulumPlugin.PLUGIN_NAME, size);
    this.x = size[0] / 2; this.y = size[1] / 2; this.vx = 0; this.vy = 0;
    this.gravity = 9.81; this.damping = 0.999; this.length = 200;
    this.ellipse_a = 150; this.ellipse_b = 100;
    this.trail_points = []; this.max_trail_length = 500;
    this.color_hue = 0; this.line_width = 2; this.color_saturation = 0.8; this.color_brightness = 0.9;
    this.audio_sensitivity = 1.0; this.beat_impulse = 0; this.beat_decay = 0.9;
    this.color_cycle_speed = 1.0; this.motion_smoothing = 0.1;
    this.parameters = {
      gravity: this.gravity, damping: this.damping, ellipse_a: this.ellipse_a, ellipse_b: this.ellipse_b,
      audio_sensitivity: this.audio_sensitivity, trail_length: this.max_trail_length, line_width: this.line_width,
      color_cycle_speed: this.color_cycle_speed, color_saturation: this.color_saturation,
      color_brightness: this.color_brightness,
    };
    this._last_beat_time = 0;
  }

  update(f, dt) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    const t = this.now();
    if (beat && t - this._last_beat_time > 0.1) {
      this.beat_impulse = Math.min(this.beat_impulse + amplitude * 10, 5.0);
      this._last_beat_time = t;
    }
    const cx = this.surface_size[0] / 2, cy = this.surface_size[1] / 2;
    const dx = this.x - cx, dy = this.y - cy;
    let fx = this.ellipse_a > 0 ? -dx * (this.gravity / this.ellipse_a) : 0;
    let fy = this.ellipse_b > 0 ? -dy * (this.gravity / this.ellipse_b) : 0;
    const tf = t * 2 * Math.PI, fi = Math.max(0.001, frequency * 0.001);
    fx += Math.sin(tf * fi) * amplitude * this.audio_sensitivity * 50;
    fy += Math.cos(tf * fi * 1.5) * amplitude * this.audio_sensitivity * 50;
    const bass = fb.bass ?? 0;
    fx += Math.cos(tf * 0.5) * bass * this.audio_sensitivity * 30;
    fy += Math.sin(tf * 0.5) * bass * this.audio_sensitivity * 30;
    if (this.beat_impulse > 0) {
      const ang = uniform(0, 2 * Math.PI), s = this.beat_impulse * 20;
      fx += Math.cos(ang) * s; fy += Math.sin(ang) * s;
      this.beat_impulse *= this.beat_decay;
    }
    this.vx += fx * dt; this.vy += fy * dt;
    this.vx *= this.damping; this.vy *= this.damping;
    this.x += this.vx * dt * 100; this.y += this.vy * dt * 100;
    const m = 50, [W, H] = this.surface_size;
    if (this.x < m) { this.x = m; this.vx = Math.abs(this.vx) * 0.8; }
    else if (this.x > W - m) { this.x = W - m; this.vx = -Math.abs(this.vx) * 0.8; }
    if (this.y < m) { this.y = m; this.vy = Math.abs(this.vy) * 0.8; }
    else if (this.y > H - m) { this.y = H - m; this.vy = -Math.abs(this.vy) * 0.8; }
    this.trail_points.push([int(this.x), int(this.y)]);
    while (this.trail_points.length > this.max_trail_length) this.trail_points.shift();
    this.color_hue += this.color_cycle_speed * dt * 30;
    this.color_hue += amplitude * 50 * this.audio_sensitivity * dt;
    if (frequency > 0) this.color_hue += frequency * 0.01 * dt;
    this.color_hue = pymod(this.color_hue, 360);
  }

  render(g) {
    const pts = this.trail_points, n = pts.length;
    if (n < 2) return;
    const b = g.blended();
    for (let i = 1; i < n; i++) {
      const alpha = (i / n) * 255, progress = i / n;
      const color = hsvToRgb(pymod(this.color_hue + progress * 60, 360), this.color_saturation, this.color_brightness);
      const w = Math.max(1, int(this.line_width * (1.0 + progress * 0.5 + this.beat_impulse * 0.3)));
      // Python: opaque line when alpha >= 255, else a line on a SRCALPHA temp surface blitted (alpha blended).
      if (alpha >= 255) g.line(color, pts[i - 1], pts[i], w);
      else b.line([...color, int(alpha)], pts[i - 1], pts[i], w);
    }
    const cur = pts[n - 1], cc = hsvToRgb(this.color_hue, 1.0, 1.0);
    const pulse = int(3 + this.beat_impulse * 2);
    for (let r = pulse; r > 0; r--) b.circle([...cc, int(255 * (r / pulse) * 0.7)], cur, r);
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'trail_length') {
      this.max_trail_length = int(value);
      while (this.trail_points.length > this.max_trail_length) this.trail_points.shift();
    } else if (name === 'ellipse_a' || name === 'ellipse_b') {
      this[name] = Math.max(10, Number(value)); this.parameters[name] = this[name];
    } else if (name === 'line_width') {
      this.line_width = Math.max(1, int(value)); this.parameters[name] = this.line_width;
    }
  }

  reset() {
    this.trail_points = [];
    this.x = this.surface_size[0] / 2; this.y = this.surface_size[1] / 2;
    this.vx = 0; this.vy = 0; this.color_hue = 0; this.beat_impulse = 0;
  }

  info() { return { 'trail points': this.trail_points.length }; }
}
