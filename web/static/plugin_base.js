// Base class and shared helpers for the JavaScript ports of the plugins in plugins/*.py.
// Contract (mirrors plugins.ArtPlugin): constructor(size) with size = [w, h]; update(features, dt); render(g) with g a
// pg.Gfx for the display surface; getParameters() -> copy of this.parameters; setParameter(name, value); reset().
// `features` uses the Python keys: amplitude, beat_detected, dominant_frequency, frequency_bands {bass, mid, treble}
// (plus the other AudioAnalyzer keys). time.time() in the Python code is this.now() here (seconds).
let clockFn = () => performance.now() / 1000;
// The app uses the wall clock (as the desktop does); tests install a simulated clock.
export function setClock(fn) { clockFn = fn; }
export const now = () => clockFn();

export class ArtPlugin {
  constructor(name, size) {
    this.name = name;
    this.surface_size = size;
    this.is_active = false;
    this.parameters = {};
    this.last_update = now();
  }
  now() { return clockFn(); }
  update(_features, _dt) {}
  render(_g) {}
  getParameters() { return { ...this.parameters }; }
  setParameter(_name, _value) {}
  reset() {}
  // Extra lines for the info box (counts of trail points, particles, ...).
  info() { return {}; }
}

// The hsv_to_rgb(h, s, v) method that most plugins define (h in degrees, s and v 0..1, ints 0..255 truncated).
export function hsvToRgb(h, s, v) {
  h = ((h % 360) + 360) % 360;
  const c = v * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = v - c;
  let r, g, b;
  if (h < 60) [r, g, b] = [c, x, 0];
  else if (h < 120) [r, g, b] = [x, c, 0];
  else if (h < 180) [r, g, b] = [0, c, x];
  else if (h < 240) [r, g, b] = [0, x, c];
  else if (h < 300) [r, g, b] = [x, 0, c];
  else [r, g, b] = [c, 0, x];
  return [Math.trunc((r + m) * 255), Math.trunc((g + m) * 255), Math.trunc((b + m) * 255)];
}

// Python's % (result has the sign of the divisor).
export const pymod = (a, n) => ((a % n) + n) % n;
export const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
// int() truncation toward zero.
export const int = v => Math.trunc(v);
// Default feature getter mirroring audio_features.get(key, default).
export const get = (f, key, dflt) => (f && f[key] !== undefined && f[key] !== null ? f[key] : dflt);
export const bands = f => get(f, 'frequency_bands', { bass: 0, mid: 0, treble: 0 });
