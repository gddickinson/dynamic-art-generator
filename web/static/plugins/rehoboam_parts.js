// Port of DataNode, DataStream and PredictionPathway from plugins/rehoboam.py.
import { get } from '../plugin_base.js';
import { uniform, random, randint } from '../pyrand.js';

export class DataNode {
  constructor(angle, radius, ring_index) {
    this.angle = angle; this.radius = radius; this.ring_index = ring_index;
    this.x = 0; this.y = 0; this.active = false; this.activation_level = 0.0;
    this.pulse_phase = uniform(0, 2 * Math.PI); this.connections = [];
    this.data_value = uniform(0, 100); this.prediction_confidence = uniform(0.3, 0.95);
    this.base_size = 3 + ring_index * 0.5; this.current_size = this.base_size; this.glow_intensity = 0.0;
    this.breathing_offset = uniform(0, 2 * Math.PI);
  }

  update_position(cx, cy) {
    this.x = cx + this.radius * Math.cos(this.angle);
    this.y = cy + this.radius * Math.sin(this.angle);
  }

  update(dt, f) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    this.pulse_phase += dt * 3;
    this.breathing_offset += dt * 2;
    const breathing = 1 + 0.1 * Math.sin(this.breathing_offset), boost = 1 + amplitude * 0.3;
    if (beat && random() < 0.3) { this.activation_level = Math.min(1.0, this.activation_level + 0.5); this.active = true; }
    this.activation_level *= 0.95;
    if (this.activation_level < 0.1) this.active = false;
    this.current_size = this.base_size * breathing * boost;
    this.glow_intensity = this.activation_level;
  }
}

export class DataStream {
  constructor(start_node, end_node) {
    this.start_node = start_node; this.end_node = end_node; this.particles = [];
    this.stream_active = false; this.flow_speed = uniform(50, 100);
    this.particle_spawn_timer = 0; this.stream_strength = uniform(0.3, 1.0);
  }

  spawn_particle() {
    this.particles.push({ progress: 0.0, speed: this.flow_speed, life: 1.0, size: uniform(1, 3), brightness: uniform(0.5, 1.0) });
  }

  update(dt, f) {
    const amplitude = get(f, 'amplitude', 0);
    this.stream_active = this.start_node.active || this.end_node.active || amplitude > 0.2 || random() < 0.1;
    if (this.stream_active) {
      this.particle_spawn_timer += dt;
      if (this.particle_spawn_timer > 0.3 / (1 + amplitude * 2)) { this.spawn_particle(); this.particle_spawn_timer = 0; }
    }
    this.particles = this.particles.filter(p => {
      p.progress += p.speed * dt / 100;
      p.life -= dt;
      if (p.progress >= 1.0 || p.life <= 0) {
        if (p.progress >= 1.0) {
          this.end_node.activation_level = Math.min(1.0, this.end_node.activation_level + 0.3);
          this.end_node.active = true;
        }
        return false;
      }
      return true;
    });
  }
}

export class PredictionPathway {
  constructor(origin_node, direction, length) {
    this.origin_node = origin_node; this.direction = direction; this.length = length;
    this.confidence = uniform(0.2, 0.9); this.active = false; this.growth_progress = 0.0;
    this.branch_points = [];
    this.probability_text = `${(this.confidence * 100).toFixed(1)}%`;
    const n = randint(1, 4);
    for (let i = 0; i < n; i++) {
      const progress = uniform(0.3, 0.9), angle = direction + uniform(-0.5, 0.5), blen = length * uniform(0.3, 0.7);
      this.branch_points.push({ progress, angle, length: blen, active: false });
    }
  }

  update(dt, f) {
    const beat = get(f, 'beat_detected', false), frequency = get(f, 'dominant_frequency', 0);
    if ((beat || frequency > 800) && random() < 0.4) { this.active = true; this.growth_progress = 0.0; }
    if (this.active) {
      this.growth_progress += dt * 2;
      for (const b of this.branch_points) if (this.growth_progress > b.progress && !b.active) b.active = true;
      if (this.growth_progress > 1.2) {
        this.active = false; this.growth_progress = 0.0;
        for (const b of this.branch_points) b.active = false;
      }
    }
  }
}
