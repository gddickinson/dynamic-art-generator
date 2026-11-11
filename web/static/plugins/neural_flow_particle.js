// FlowParticle from plugins/neural_flow.py: a particle drifting through the flow field, clustering with its neighbours.
import { get, bands, int, pymod } from '../plugin_base.js';
import { uniform } from '../pyrand.js';

export class FlowParticle {
  constructor(x, y) {
    this.x = x; this.y = y;
    this.vx = uniform(-10, 10); this.vy = uniform(-10, 10);
    this.life = uniform(3, 8); this.max_life = this.life;
    this.energy = uniform(0.5, 1.0);
    this.size = uniform(0.5, 2.5); this.base_size = this.size;
    this.flow_strength = uniform(0.3, 1.0);
    this.viscosity = uniform(0.95, 0.99);
    this.cluster_affinity = uniform(0.1, 0.8);
    this.opacity = 1.0;
    this.color_offset = uniform(0, 60);
    this.pulse_phase = uniform(0, 2 * Math.PI);
    this.breathing_rate = uniform(1, 3);
    this.clustering_scale = 1.0; this.breathing_scale = 1.0;   // plugin clustering_strength / organic_breathing
    this.connections = []; this.is_cluster_center = false; this.cluster_strength = 0;
    this.trail = []; this.max_trail = 8;
  }

  // flowField: { rows, cols, data: Float64Array(rows*cols*2) }
  update(dt, flowField, f, bounds, others) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false), fb = bands(f);
    this.life -= dt;
    this.energy += amplitude * 0.5 * dt;
    this.energy = Math.min(1.5, this.energy * 0.98);
    if (beat) { this.energy += amplitude * 2; this.size = this.base_size * (1 + amplitude); }
    const gx = pymod(int(this.x / 20), flowField.cols), gy = pymod(int(this.y / 20), flowField.rows);
    const k = (gy * flowField.cols + gx) * 2;
    this.vx += flowField.data[k] * this.flow_strength * dt * 100;
    this.vy += flowField.data[k + 1] * this.flow_strength * dt * 100;
    if (this.clustering_scale > 0) this.applyClusteringForces(others, dt, amplitude);
    const bassForce = (fb.bass ?? 0) * 30;
    if (bassForce > 0) {
      const dx = this.x - bounds[0] / 2, dy = this.y - bounds[1] / 2;
      const dist = Math.sqrt(dx * dx + dy * dy) + 1;
      this.vx += (dx / dist) * bassForce * dt;
      this.vy += (dy / dist) * bassForce * dt;
    }
    const trebleForce = (fb.treble ?? 0) * 20;
    if (trebleForce > 0) {
      const ang = Math.atan2(this.vy, this.vx) + trebleForce * dt;
      this.vx += Math.cos(ang) * trebleForce * dt;
      this.vy += Math.sin(ang) * trebleForce * dt;
    }
    this.vx *= this.viscosity; this.vy *= this.viscosity;
    this.x += this.vx * dt; this.y += this.vy * dt;
    const m = 20;
    if (this.x < -m) this.x = bounds[0] + m; else if (this.x > bounds[0] + m) this.x = -m;
    if (this.y < -m) this.y = bounds[1] + m; else if (this.y > bounds[1] + m) this.y = -m;
    const lr = this.life / this.max_life;
    this.opacity = lr * this.energy;
    this.pulse_phase += this.breathing_rate * dt;
    this.size = this.base_size * (1 + 0.2 * this.breathing_scale * Math.sin(this.pulse_phase)) * (0.5 + 0.5 * lr);
    this.trail.push([this.x, this.y]);
    if (this.trail.length > this.max_trail) this.trail.shift();
    this.updateClusterStatus(others);
  }

  applyClusteringForces(others, dt, _amplitude) {
    let fx = 0, fy = 0;
    for (const o of others) {
      if (o === this) continue;
      const dx = o.x - this.x, dy = o.y - this.y, d = Math.sqrt(dx * dx + dy * dy);
      if (d > 0 && d < 80) {
        const att = this.cluster_affinity * o.cluster_affinity * 10 / (d + 1) * this.clustering_scale;
        fx += (dx / d) * att; fy += (dy / d) * att;
        if (d < 15) {
          const rep = 50 / (d * d + 1);
          fx -= (dx / d) * rep; fy -= (dy / d) * rep;
        }
      }
    }
    this.vx += fx * dt; this.vy += fy * dt;
  }

  updateClusterStatus(others) {
    let near = 0;
    for (const o of others) {
      if (o === this) continue;
      const dx = o.x - this.x, dy = o.y - this.y;
      if (Math.sqrt(dx * dx + dy * dy) < 40) near++;
    }
    this.is_cluster_center = near > 5;
    this.cluster_strength = Math.min(1.0, near / 10.0);
  }

  isAlive() { return this.life > 0; }
}
