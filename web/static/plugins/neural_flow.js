// Port of plugins/neural_flow.py (NeuralFlowPlugin): breathing clusters of particles in a flow field, joined by
// neural-like connections. FlowParticle lives in neural_flow_particle.js.
import { ArtPlugin, hsvToRgb, get, int, pymod, clamp } from '../plugin_base.js';
import { uniform, randint, random, choice } from '../pyrand.js';
import { FlowParticle } from './neural_flow_particle.js';

// Several shapes drawn onto ONE SRCALPHA temp surface overwrite each other's pixels (pygame draw does not blend).
// Drawing them in the same order with alpha (a_new - a_prev) / (1 - a_prev) composites to the overwritten alpha.
const stackAlpha = (a, prev) => (prev >= 255 ? 0 : ((a - prev) / (255 - prev)) * 255);

export class NeuralFlowPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Neural Flow';
  static PLUGIN_DESCRIPTION = 'Organic particle networks inspired by AMIANGELIKA';
  static SOURCE = 'plugins/neural_flow.py';

  constructor(size) {
    super(NeuralFlowPlugin.PLUGIN_NAME, size);
    this.particles = []; this.max_particles = 800; this.spawn_rate = 30; this.spawn_timer = 0;
    this.flow_field_size = [30, 40];
    this.flow_field = { rows: 30, cols: 40, data: new Float64Array(30 * 40 * 2) };
    this.flow_time = 0; this.flow_speed = 0.5;
    this.viscosity = 0.98; this.clustering_strength = 1.0; this.flow_turbulence = 0.3; this.organic_breathing = 1.0;
    this.particle_opacity = 0.8; this.connection_threshold = 60; this.trail_length = 0.5; this.glow_intensity = 0.6;
    this.base_hue = 300; this.color_variance = 30; this.color_evolution_speed = 10; this.monochrome_mode = true;
    this.audio_sensitivity = 1.2; this.beat_response_strength = 2.0; this.frequency_flow_influence = 1.0;
    this.enable_clustering = true; this.enable_flow_field = true; this.enable_connections = true;
    this.enable_breathing = true; this.enable_trails = true;
    this.parameters = {
      max_particles: this.max_particles, spawn_rate: this.spawn_rate, clustering_strength: this.clustering_strength,
      flow_turbulence: this.flow_turbulence, organic_breathing: this.organic_breathing,
      particle_opacity: this.particle_opacity, connection_threshold: this.connection_threshold,
      glow_intensity: this.glow_intensity, audio_sensitivity: this.audio_sensitivity,
      beat_response_strength: this.beat_response_strength, color_variance: this.color_variance,
      monochrome_mode: this.monochrome_mode, enable_clustering: this.enable_clustering,
      enable_flow_field: this.enable_flow_field, enable_connections: this.enable_connections,
    };
    this.generateFlowField();
    this.spawnInitialParticles();
  }

  generateFlowField() {
    const { rows, cols, data } = this.flow_field;
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const nx = (x * 0.1 + this.flow_time * this.flow_speed) * 2 * Math.PI;
        const ny = (y * 0.1 + this.flow_time * this.flow_speed * 0.7) * 2 * Math.PI;
        const ang = Math.sin(nx) * Math.cos(ny) + 0.5 * Math.sin(nx * 2) * Math.sin(ny * 1.5) +
          0.3 * Math.cos(nx * 0.5) * Math.cos(ny * 0.8);
        const mag = (0.3 + 0.7 * Math.abs(Math.sin(nx + ny))) * this.flow_turbulence;
        const k = (y * cols + x) * 2;
        data[k] = Math.cos(ang) * mag; data[k + 1] = Math.sin(ang) * mag;
      }
    }
  }

  spawnInitialParticles() {
    const [W, H] = this.surface_size;
    for (const [cx, cy] of [[W * 0.3, H * 0.4], [W * 0.7, H * 0.6], [W * 0.5, H * 0.3]]) {
      const cs = uniform(30, 80), density = randint(20, 40);
      for (let i = 0; i < density; i++) {
        const a = uniform(0, 2 * Math.PI), d = uniform(0, cs);
        const p = new FlowParticle(cx + d * Math.cos(a), cy + d * Math.sin(a));
        p.cluster_affinity = uniform(0.6, 1.0);
        this.particles.push(p);
      }
    }
  }

  update(f, dt) {
    this.flow_time += dt;
    const amplitude = get(f, 'amplitude', 0) * this.audio_sensitivity;
    const frequency = get(f, 'dominant_frequency', 0);
    if (this.enable_flow_field) {
      const old = this.flow_turbulence;
      this.flow_turbulence = old + amplitude * 0.5;
      this.generateFlowField();
      this.flow_turbulence = old;
    }
    this.base_hue += this.color_evolution_speed * dt;
    if (frequency > 0) this.base_hue += frequency * 0.01 * dt;
    this.base_hue = pymod(this.base_hue, 360);
    this.spawnParticles(f, dt);
    for (const p of [...this.particles]) {
      if (p.isAlive()) {
        p.clustering_scale = this.enable_clustering ? this.clustering_strength : 0; p.breathing_scale = this.organic_breathing;
        p.update(dt, this.flow_field, f, this.surface_size, this.particles);
      } else this.particles.splice(this.particles.indexOf(p), 1);
    }
    while (this.particles.length < this.max_particles * 0.8) this.spawnSingleParticle(amplitude);
  }

  spawnParticles(f, dt) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const rate = this.spawn_rate + amplitude * 50 + (beat ? 20 : 0);
    this.spawn_timer += dt;
    const interval = 1.0 / Math.max(1, rate);
    let n = 0;
    while (this.spawn_timer >= interval && this.particles.length < this.max_particles) {
      n++; this.spawn_timer -= interval;
      if (n > 30) break;
    }
    for (let i = 0; i < n; i++) this.spawnSingleParticle(amplitude);
  }

  spawnSingleParticle(amplitude) {
    let x, y;
    if (this.particles.length && random() < 0.7) {
      const s = choice(this.particles), a = uniform(0, 2 * Math.PI), d = uniform(10, 40);
      x = s.x + d * Math.cos(a); y = s.y + d * Math.sin(a);
    } else {
      x = uniform(0, this.surface_size[0]); y = uniform(0, this.surface_size[1]);
    }
    const p = new FlowParticle(x, y);
    p.energy += amplitude * 0.5; p.flow_strength += amplitude * 0.3;
    this.particles.push(p);
  }

  render(g) {
    const b = g.blended();
    if (this.enable_connections) this.renderConnections(b);
    if (this.enable_trails) this.renderTrails(b);
    this.renderParticles(b);
    this.renderClusterCenters(b);
  }

  renderConnections(b) {
    const ps = this.particles, thr = this.connection_threshold;
    for (let i = 0; i < ps.length; i++) {
      const p = ps[i];
      if (!p.isAlive()) continue;
      let drawn = 0;
      for (let j = i + 1; j < ps.length; j++) {
        const o = ps[j];
        if (!o.isAlive() || drawn >= 3) continue;
        const dx = o.x - p.x, dy = o.y - p.y, d = Math.sqrt(dx * dx + dy * dy);
        if (d < thr) {
          const s = (1 - d / thr) * p.cluster_affinity * o.cluster_affinity;
          if (s > 0.1) { this.drawConnection(b, p, o, s); drawn++; }
        }
      }
    }
  }

  drawConnection(b, p1, p2, strength) {
    const col = this.monochrome_mode ? hsvToRgb(this.base_hue, 0.6, 0.8)
      : hsvToRgb(pymod(this.base_hue + (p1.color_offset + p2.color_offset) / 2, 360), 0.7, 0.9);
    const alpha = clamp(int(strength * (p1.energy + p2.energy) * 0.5 * 255 * this.particle_opacity), 0, 255);
    if (alpha <= 20) return;
    uniform(-5, 5); uniform(-5, 5);   // the unused curve midpoint in Python still draws two random numbers
    const s = [int(p1.x), int(p1.y)], e = [int(p2.x), int(p2.y)];
    let prev = 0;
    for (const t of [3, 2, 1]) {        // glow: three lines on one temp surface (later ones overwrite)
      const la = Math.floor(alpha / (t + 1));
      if (la > 0) { b.line([...col, stackAlpha(la, prev)], s, e, t); prev = la; }
    }
  }

  renderTrails(b) {
    for (const p of this.particles) {
      const n = p.trail.length;
      if (n < 2) continue;
      const col = this.monochrome_mode ? hsvToRgb(this.base_hue, 0.4, 0.6)
        : hsvToRgb(pymod(this.base_hue + p.color_offset, 360), 0.5, 0.7);
      for (let i = 1; i < n; i++) {
        const ts = (i / n) * this.trail_length;
        if (ts <= 0.1) continue;
        const a = clamp(int(ts * p.opacity * 255), 0, 255);
        if (a > 10) b.circle([...col, a], [int(p.trail[i][0]), int(p.trail[i][1])], 2);
      }
    }
  }

  renderParticles(b) {
    for (const p of this.particles) {
      if (!p.isAlive()) continue;
      const pos = [int(p.x), int(p.y)];
      const col = this.monochrome_mode ? hsvToRgb(this.base_hue, 0.8, 0.9)
        : hsvToRgb(pymod(this.base_hue + p.color_offset, 360), 0.8, 0.9);
      const size = Math.max(1, int(p.size));
      const alpha = clamp(int(p.opacity * 255 * this.particle_opacity), 0, 255);
      if (alpha <= 10) continue;
      const gs = size + 3, ga = int(alpha * this.glow_intensity * 0.3);
      if (ga > 0) {
        // Python: filled circles r = gs..1 on one temp surface, each overwriting the centre with a lower alpha;
        // the result is a set of 1-px annuli, ring r carrying alpha ga*r/gs.
        for (let r = gs; r > 0; r--) {
          const ra = int(ga * (r / gs));
          if (ra > 0) b.circle([...col, ra], pos, r, 1);
        }
      }
      b.circle([...col, alpha], pos, size);
    }
  }

  renderClusterCenters(b) {
    for (const p of this.particles) {
      if (!(p.is_cluster_center && p.cluster_strength > 0.3)) continue;
      const cs = int(8 + p.cluster_strength * 6), ca = int(p.cluster_strength * 150);
      if (ca > 20) b.circle([...hsvToRgb(this.base_hue, 1.0, 1.0), ca], [int(p.x), int(p.y)], cs, 2);
    }
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'max_particles') {
      this.max_particles = Math.max(50, Math.min(2000, int(value)));
      while (this.particles.length > this.max_particles) this.particles.shift();
      this.parameters[name] = this.max_particles;
    } else if (name === 'particle_opacity' || name === 'glow_intensity' || name === 'trail_length') {
      this[name] = Math.max(0, Math.min(1, Number(value))); this.parameters[name] = this[name];
    } else if (name === 'monochrome_mode') {
      this.monochrome_mode = Boolean(value); this.parameters[name] = this.monochrome_mode;
    }
  }

  reset() {
    this.particles = [];
    this.flow_time = 0; this.generateFlowField();
    this.base_hue = 300;
    this.spawnInitialParticles();
  }

  info() { return { particles: this.particles.length, 'cluster centres': this.particles.filter(p => p.is_cluster_center).length }; }
}
