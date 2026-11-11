// Port of plugins/noise_sphere.py (NoiseSpherePlugin): a 3D sphere covered in thousands of noise-driven hairs.
import { ArtPlugin, hsvToRgb, get, bands, int, pymod } from '../plugin_base.js';
import { uniform } from '../pyrand.js';

// NoiseGenerator: sum of octaves of a sin/cos "noise".
class NoiseGenerator {
  constructor(octaves = 4, persistence = 0.5) { this.octaves = octaves; this.persistence = persistence; }
  noise(x, y = 0, z = 0) {
    let value = 0, amp = 1, freq = 1;
    for (let o = 0; o < this.octaves; o++) {
      value += amp * this._simple(x * freq, y * freq, z * freq);
      amp *= this.persistence; freq *= 2;
    }
    return value;
  }
  _simple(x, y, z) {
    return Math.sin(x * 1.5 + Math.cos(y * 2.3)) * Math.cos(y * 1.7 + Math.sin(z * 1.9)) *
      Math.sin(z * 2.1 + Math.cos(x * 1.3)) * 0.5;
  }
}

class Hair {
  constructor(radius, noiseGen) {
    this.noise_gen = noiseGen;
    this.z = uniform(-radius, radius);
    this.phi = uniform(0, 2 * Math.PI);
    this.theta = radius > 0 ? Math.asin(this.z / radius) : 0;
    this.length_multiplier = uniform(1.15, 1.2);
    this.base_length = this.length_multiplier;
    this.thickness = uniform(0.5, 2.0);
    this.noise_offset_phi = uniform(0, 1000);
    this.noise_offset_theta = uniform(0, 1000);
    this.color_offset = uniform(0, 360);
    this.energy = 0; this.beat_response = 0;
    this.base_x = this.base_y = this.base_z = this.tip_x = this.tip_y = this.tip_z = 0;
  }

  update(radius, tf, f, dt) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    this.energy += amplitude * 5 * dt;
    this.energy *= 0.95;
    if (beat) this.beat_response = Math.min(this.beat_response + amplitude * 3, 2.0);
    else this.beat_response *= 0.9;
    const nt = tf * 0.0005, ng = this.noise_gen;
    let offPhi = (ng.noise(nt, Math.sin(this.phi) + this.noise_offset_phi) - 0.5) * 0.3;
    let offTheta = (ng.noise(nt * 0.7, Math.sin(this.z) * 0.01 + this.noise_offset_theta) - 0.5) * 0.3;
    offPhi += (fb.bass ?? 0) * 0.5 * Math.sin(tf * 0.01);
    offTheta += (fb.treble ?? 0) * 0.3 * Math.cos(tf * 0.007);
    this.theta_current = this.theta + offTheta;
    this.phi_current = this.phi + offPhi;
    const ct = Math.cos(this.theta);
    this.base_x = radius * ct * Math.cos(this.phi);
    this.base_y = radius * ct * Math.sin(this.phi);
    this.base_z = radius * Math.sin(this.theta);
    const len = radius * this.length_multiplier * (1 + this.energy * 0.2 + this.beat_response * 0.3);
    const cc = Math.cos(this.theta_current);
    this.tip_x = len * cc * Math.cos(this.phi_current);
    this.tip_y = len * cc * Math.sin(this.phi_current);
    this.tip_z = len * Math.sin(this.theta_current);
    this.color_offset += (frequency > 0 ? frequency * 0.1 : 0) * dt;
    this.color_offset = pymod(this.color_offset, 360);
  }
}

export class NoiseSpherePlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Noise Sphere';
  static PLUGIN_DESCRIPTION = '3D hairy sphere with organic Perlin noise movement';
  static SOURCE = 'plugins/noise_sphere.py';

  constructor(size) {
    super(NoiseSpherePlugin.PLUGIN_NAME, size);
    this.radius = Math.min(...size) / 3.5;
    this.hair_count = 8000; this.hairs = [];
    this.rotation_x = 0; this.rotation_y = 0; this.rotation_speed = 1.0; this.auto_rotate = true;
    this.noise_gen = new NoiseGenerator(3, 0.5); this.noise_detail = 3; this.noise_speed = 1.0;
    this.background_color = [5, 5, 15]; this.sphere_color = [0, 0, 0];
    this.hair_base_color = [0, 0, 0]; this.hair_tip_color = [200, 200, 200];
    this.show_sphere = true; this.hair_alpha = 150;
    this.base_hue = 180; this.hue_shift_speed = 30; this.color_variance = 60; this.rainbow_mode = true;
    this.audio_sensitivity = 1.0; this.beat_sensitivity = 2.0; this.frequency_response = 1.0;
    this.time_factor = 0;
    this.parameters = {
      hair_count: this.hair_count, radius: this.radius, audio_sensitivity: this.audio_sensitivity,
      beat_sensitivity: this.beat_sensitivity, frequency_response: this.frequency_response,
      noise_speed: this.noise_speed, rotation_speed: this.rotation_speed, auto_rotate: this.auto_rotate,
      show_sphere: this.show_sphere, rainbow_mode: this.rainbow_mode, hair_alpha: this.hair_alpha,
      hue_shift_speed: this.hue_shift_speed,
    };
    this.createHairs();
  }

  createHairs() {
    this.hairs = [];
    for (let i = 0; i < int(this.hair_count); i++) this.hairs.push(new Hair(this.radius, this.noise_gen));
  }

  update(f, dt) {
    this.time_factor += dt * 1000;
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    const scaled = {
      amplitude: amplitude * this.audio_sensitivity, beat_detected: beat,
      dominant_frequency: frequency * this.frequency_response,
      frequency_bands: { bass: fb.bass ?? 0, mid: fb.mid ?? 0, treble: fb.treble ?? 0 },
    };
    if (this.auto_rotate) {
      const rs = this.rotation_speed * (1 + amplitude * 0.5);
      this.rotation_y += rs * dt * 0.5;
      this.rotation_x += rs * dt * 0.3;
    }
    if (this.rainbow_mode) {
      this.base_hue = pymod(this.base_hue + this.hue_shift_speed * dt, 360);
      if (frequency > 0) this.base_hue = pymod(this.base_hue + frequency * 0.01 * dt, 360);
    }
    const r = this.radius * (1 + amplitude * 0.2);
    const tf = this.time_factor * this.noise_speed;
    for (const h of this.hairs) h.update(r, tf, scaled, dt);
  }

  render(g) {
    g.fill(this.background_color);
    const cx = this.surface_size[0] / 2, cy = this.surface_size[1] / 2;
    if (this.show_sphere) g.circle(this.sphere_color, [int(cx), int(cy)], Math.max(3, int(this.radius * 0.8)));
    this.renderHairs(g, cx, cy);
  }

  // Rotation, projection and back-to-front sort into reusable typed arrays (no per-hair objects per frame).
  renderHairs(g, cx, cy) {
    const n = this.hairs.length;
    if (!this._buf || this._buf.n !== n) {
      this._buf = { n, bx: new Int32Array(n), by: new Int32Array(n), tx: new Int32Array(n), ty: new Int32Array(n),
        depth: new Float64Array(n), order: new Uint32Array(n) };
    }
    const B = this._buf;
    const cX = Math.cos(this.rotation_x), sX = Math.sin(this.rotation_x);
    const cY = Math.cos(this.rotation_y), sY = Math.sin(this.rotation_y);
    for (let i = 0; i < n; i++) {
      const h = this.hairs[i];
      // rotate_3d: around X, then around Y; project_to_2d: orthographic, int()
      let y = h.base_y * cX - h.base_z * sX, z = h.base_y * sX + h.base_z * cX;
      B.bx[i] = int(cx + h.base_x * cY + z * sY); B.by[i] = int(cy + y);
      y = h.tip_y * cX - h.tip_z * sX; z = h.tip_y * sX + h.tip_z * cX;
      B.tx[i] = int(cx + h.tip_x * cY + z * sY); B.ty[i] = int(cy + y);
      B.depth[i] = -h.tip_x * sY + z * cY;
      B.order[i] = i;
    }
    B.order.sort((a, b) => B.depth[a] - B.depth[b] || a - b);   // stable, back to front
    const opaque = this.hair_alpha >= 255, dst = opaque ? g : g.blended();
    const [W, H] = this.surface_size, ctx = g.ctx;
    let runKey = null;
    const flush = () => { if (runKey !== null) { ctx.stroke(); runKey = null; } };
    for (let k = 0; k < n; k++) {
      const i = B.order[k], h = this.hairs[i], depth = B.depth[i];
      let col;
      if (this.rainbow_mode) col = hsvToRgb(pymod(this.base_hue + h.color_offset + depth * 0.5, 360), 0.8, 0.9);
      else {
        const df = Math.max(0, Math.min(1, (depth + this.radius) / (2 * this.radius)));
        const gv = int(50 + df * 150 + h.energy * 50);
        col = [gv, gv, gv];
      }
      if (h.beat_response > 0.1) col = col.map(c => Math.min(255, int(c * (1 + h.beat_response * 0.5))));
      // pygame raises ValueError for a colour component > 255 and the Python code skips that hair.
      if (col[0] > 255 || col[1] > 255 || col[2] > 255) continue;
      const th = Math.max(1, int(h.thickness + h.energy * 0.5));
      const bx = B.bx[i], by = B.by[i], tx = B.tx[i], ty = B.ty[i];
      if (!(bx >= 0 && bx <= W && by >= 0 && by <= H && tx >= 0 && tx <= W * 2 && ty >= 0 && ty <= H * 2)) continue;
      if (!opaque) { dst.line([...col, this.hair_alpha], [bx, by], [tx, ty], th); continue; }
      // Opaque: consecutive hairs of the same colour and width share one path (identical pixels).
      const key = `${col[0]},${col[1]},${col[2]},${th}`;
      if (key !== runKey) {
        flush();
        ctx.beginPath(); ctx.lineWidth = th; ctx.lineCap = th > 2 ? 'round' : 'butt'; ctx.strokeStyle = g.col(col);
        runKey = key;
      }
      ctx.moveTo(bx, by); ctx.lineTo(tx, ty);
    }
    flush();
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'hair_count') {
      const nc = Math.max(100, Math.min(20000, int(value)));
      if (nc !== this.hairs.length) { this.hair_count = nc; this.createHairs(); this.parameters[name] = nc; }
    } else if (name === 'radius') {
      this.radius = Math.max(50, Math.min(Math.min(...this.surface_size) / 2, Number(value)));
      this.parameters[name] = this.radius;
      this.createHairs();
    } else if (name === 'audio_sensitivity' || name === 'beat_sensitivity' || name === 'frequency_response') {
      this[name] = Math.max(0, Math.min(5, Number(value))); this.parameters[name] = this[name];
    } else if (name === 'hair_alpha') {
      this.hair_alpha = Math.max(10, Math.min(255, int(value))); this.parameters[name] = this.hair_alpha;
    }
  }

  reset() {
    this.rotation_x = 0; this.rotation_y = 0; this.time_factor = 0; this.base_hue = 180;
    for (const h of this.hairs) { h.energy = 0; h.beat_response = 0; }
  }

  info() { return { hairs: this.hairs.length }; }
}
