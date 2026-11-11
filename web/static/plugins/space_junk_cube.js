// Vector3D and Cube3D from plugins/space_junk.py.
import { hsvToRgb, get, bands, int, pymod, now } from '../plugin_base.js';
import { uniform } from '../pyrand.js';

export class Vector3D {
  constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
  rotate_x(a) { const c = Math.cos(a), s = Math.sin(a); return new Vector3D(this.x, this.y * c - this.z * s, this.y * s + this.z * c); }
  rotate_y(a) { const c = Math.cos(a), s = Math.sin(a); return new Vector3D(this.x * c + this.z * s, this.y, -this.x * s + this.z * c); }
  rotate_z(a) { const c = Math.cos(a), s = Math.sin(a); return new Vector3D(this.x * c - this.y * s, this.x * s + this.y * c, this.z); }
  // Perspective projection; returns null where Python raises ZeroDivisionError (fov + z == 0).
  project(w, h, fov = 500) {
    if (this.z === 0) this.z = 0.001;
    if (fov + this.z === 0) return null;
    const factor = fov / (fov + this.z);
    return [[int(this.x * factor + w / 2), int(this.y * factor + h / 2)], factor];
  }
}

export const FACES = [[0, 1, 2, 3], [5, 4, 7, 6], [4, 0, 3, 7], [1, 5, 6, 2], [3, 2, 6, 7], [4, 5, 1, 0]];
const BASE_COLORS = [[255, 100, 100], [100, 255, 100], [100, 100, 255], [255, 255, 100], [255, 100, 255], [100, 255, 255]];

export class Cube3D {
  constructor(w, h, d, x, y, z) {
    this.size = new Vector3D(w, h, d);
    this.position = new Vector3D(x, y, z);
    this.rotation = new Vector3D(0, 0, 0);
    this.rotation_speed = new Vector3D(uniform(0.5, 2.0), uniform(0.5, 2.0), uniform(0.5, 2.0));
    this.audio_scale = 1.0;
    this.color_shift = uniform(0, 360);
    this.energy = 0.0;
    this.pulse_phase = uniform(0, 2 * Math.PI);
    this.vertices = [
      new Vector3D(-w / 2, -h / 2, -d / 2), new Vector3D(w / 2, -h / 2, -d / 2),
      new Vector3D(w / 2, h / 2, -d / 2), new Vector3D(-w / 2, h / 2, -d / 2),
      new Vector3D(-w / 2, -h / 2, d / 2), new Vector3D(w / 2, -h / 2, d / 2),
      new Vector3D(w / 2, h / 2, d / 2), new Vector3D(-w / 2, h / 2, d / 2),
    ];
    this.faces = FACES;
    this.base_colors = BASE_COLORS;
  }

  update(dt, f, _globalRotation) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    this.energy += amplitude * 10 * dt;
    this.energy *= 0.95;
    if (beat) {
      this.energy += amplitude * 20;
      this.rotation_speed.x += uniform(-1, 1) * amplitude;
      this.rotation_speed.y += uniform(-1, 1) * amplitude;
      this.rotation_speed.z += uniform(-1, 1) * amplitude;
    }
    const sm = 1 + amplitude * 2 + this.energy * 0.1;
    this.rotation.x += this.rotation_speed.x * dt * sm;
    this.rotation.y += this.rotation_speed.y * dt * sm;
    this.rotation.z += this.rotation_speed.z * dt * sm;
    this.audio_scale = (1 + (fb.bass ?? 0) * 0.5) * (1 + 0.2 * Math.sin(this.pulse_phase + now() * 5));
    if (frequency > 0) this.color_shift += frequency * 0.01 * dt;
    this.color_shift += amplitude * 100 * dt;
    this.color_shift = pymod(this.color_shift, 360);
    this.rotation_speed.x *= 0.99; this.rotation_speed.y *= 0.99; this.rotation_speed.z *= 0.99;
  }

  getTransformedVertices(gr) {
    return this.vertices.map(v => {
      let r = new Vector3D(v.x * this.audio_scale, v.y * this.audio_scale, v.z * this.audio_scale);
      r = r.rotate_x(this.rotation.x).rotate_y(this.rotation.y).rotate_z(this.rotation.z);
      r = r.rotate_x(gr.x).rotate_y(gr.y);
      return new Vector3D(r.x + this.position.x, r.y + this.position.y, r.z + this.position.z);
    });
  }

  getFaceColor(i, lighting) {
    const base = this.base_colors[i], audio = hsvToRgb(pymod(this.color_shift + i * 60, 360), 0.8, 0.9);
    const bf = 0.7;
    const mixed = [0, 1, 2].map(k => int(base[k] * (1 - bf) + audio[k] * bf));
    const br = Math.max(0.3, Math.min(1.5, lighting + this.energy * 0.1));
    return mixed.map(c => Math.min(255, int(c * br)));
  }
}
