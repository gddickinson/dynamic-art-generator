// Port of plugins/rehoboam.py (RehoboamPlugin): concentric rings of data nodes, flowing data streams, branching
// prediction pathways and a pulsing core (Westworld-inspired).
import { ArtPlugin, get, bands, int } from '../plugin_base.js';
import { uniform, random, choice } from '../pyrand.js';
import { TAU } from '../pg.js';
import { DataNode, DataStream, PredictionPathway } from './rehoboam_parts.js';

const pct = v => `${(v * 100).toFixed(1)}%`;

export class RehoboamPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Rehoboam';
  static PLUGIN_DESCRIPTION = 'Westworld-inspired AI network visualization';
  static SOURCE = 'plugins/rehoboam.py';

  constructor(size) {
    super(RehoboamPlugin.PLUGIN_NAME, size);
    this.rings = []; this.num_rings = 6; this.nodes_per_ring = [8, 12, 16, 20, 24, 28];
    this.ring_spacing = 40; this.base_radius = 60;
    this.all_nodes = []; this.data_streams = []; this.prediction_pathways = [];
    this.center_x = size[0] / 2; this.center_y = size[1] / 2;
    this.primary_color = [0, 150, 255]; this.secondary_color = [255, 255, 255];
    this.accent_color = [255, 100, 100]; this.background_color = [5, 10, 20];
    this.global_pulse = 0; this.network_breathing = 0; this.reorganization_timer = 0;
    this.alert_mode = false; this.alert_intensity = 0.0;
    this.audio_sensitivity = 1.0; this.beat_response_strength = 1.5; this.frequency_color_shift = 0.3;
    this.network_activity_level = 0.5; this.prediction_frequency = 0.3; this.data_flow_speed = 1.0;
    this.geometric_precision = 1.0;
    this.parameters = {
      num_rings: this.num_rings, audio_sensitivity: this.audio_sensitivity,
      beat_response_strength: this.beat_response_strength, network_activity_level: this.network_activity_level,
      prediction_frequency: this.prediction_frequency, data_flow_speed: this.data_flow_speed,
      frequency_color_shift: this.frequency_color_shift, geometric_precision: this.geometric_precision,
    };
    this.build_network();
  }

  build_network() {
    this.rings = []; this.all_nodes = []; this.data_streams = []; this.prediction_pathways = [];
    for (let ri = 0; ri < int(this.num_rings); ri++) {
      const ring = [], count = ri < this.nodes_per_ring.length ? this.nodes_per_ring[ri] : 20;
      const radius = this.base_radius + ri * this.ring_spacing;
      for (let ni = 0; ni < count; ni++) {
        const node = new DataNode(2 * Math.PI * ni / count + ri * 0.1, radius, ri);
        node.update_position(this.center_x, this.center_y);
        ring.push(node); this.all_nodes.push(node);
      }
      this.rings.push(ring);
    }
    this.create_data_streams();
    this.create_prediction_pathways();
  }

  create_data_streams() {
    for (const ring of this.rings) {
      ring.forEach((node, i) => {
        const next = ring[(i + 1) % ring.length];
        if (random() < 0.7) this.data_streams.push(new DataStream(node, next));
      });
    }
    for (let ri = 0; ri < this.rings.length - 1; ri++) {
      const outer = this.rings[ri + 1];
      for (const inner of this.rings[ri]) {
        const closest = [...outer].sort((a, b) => Math.abs(a.angle - inner.angle) - Math.abs(b.angle - inner.angle)).slice(0, 3);
        for (const o of closest) if (random() < 0.4) this.data_streams.push(new DataStream(inner, o));
      }
    }
    for (let k = 0; k < 20; k++) {
      const a = choice(this.all_nodes), b = choice(this.all_nodes);
      if (a !== b && random() < 0.1) this.data_streams.push(new DataStream(a, b));
    }
  }

  create_prediction_pathways() {
    for (const node of this.all_nodes) {
      if (random() < 0.3) {
        const dir = node.angle + uniform(-0.3, 0.3), len = uniform(50, 150);
        this.prediction_pathways.push(new PredictionPathway(node, dir, len));
      }
    }
  }

  update(f, dt) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    const scaled = amplitude * this.audio_sensitivity;
    this.global_pulse += dt * 4; this.network_breathing += dt * 1.5;
    if (beat) {
      if (random() < 0.3) this.trigger_reorganization();
      for (let k = 0; k < int(this.beat_response_strength * 5); k++) {
        const node = choice(this.all_nodes);
        node.activation_level = Math.min(1.0, node.activation_level + scaled);
        node.active = true;
      }
    }
    if (frequency > 1000) { this.alert_mode = true; this.alert_intensity = Math.min(1.0, frequency / 2000); }
    else { this.alert_mode = false; this.alert_intensity *= 0.9; }
    this.network_breathing_amplitude = 0.05 + (fb.bass ?? 0) * 0.1;
    for (const node of this.all_nodes) {
      node.update(dt, f);
      const bf = 1 + this.network_breathing_amplitude * Math.sin(this.network_breathing);
      node.radius = (this.base_radius + node.ring_index * this.ring_spacing) * bf;
      node.update_position(this.center_x, this.center_y);
    }
    for (const s of this.data_streams) s.update(dt, f);
    for (const p of this.prediction_pathways) p.update(dt, f);
    this.reorganization_timer += dt;
    if (this.reorganization_timer > 10 + uniform(-2, 2)) { this.trigger_reorganization(); this.reorganization_timer = 0; }
  }

  trigger_reorganization() {
    for (const ring of this.rings) {
      if (random() < 0.5) { const r = uniform(-0.2, 0.2); for (const n of ring) n.angle += r; }
    }
    for (const p of this.prediction_pathways) if (random() < 0.4) { p.active = true; p.growth_progress = 0.0; }
  }

  render(g) {
    this.render_rings(g);
    this.render_data_streams(g);
    this.render_prediction_pathways(g);
    this.render_nodes(g);
    this.render_core(g);
    this.render_data_overlay(g);
  }

  render_rings(g) {
    const b = g.blended();
    this.rings.forEach((ring, ri) => {
      if (!ring.length) return;
      const r = ring[0].radius;
      const c = this.alert_mode ? this.blend_colors(this.primary_color, this.accent_color, this.alert_intensity) : this.primary_color;
      b.circle([...c, Math.max(50, 150 - ri * 20)], [this.center_x, this.center_y], int(r), 1);
    });
  }

  render_data_streams(g) {
    for (const s of this.data_streams) {
      if (!s.stream_active && !s.particles.length) continue;
      const a = s.start_node, e = s.end_node;
      g.line(this.primary_color, [int(a.x), int(a.y)], [int(e.x), int(e.y)], 1);
      for (const p of s.particles) {
        const x = a.x + p.progress * (e.x - a.x), y = a.y + p.progress * (e.y - a.y);
        const c = this.brighten_color(this.primary_color, p.brightness * p.life);
        g.circle(c, [int(x), int(y)], Math.max(1, int(p.size)));
      }
    }
  }

  render_prediction_pathways(g) {
    for (const p of this.prediction_pathways) {
      if (!p.active) continue;
      const sx = p.origin_node.x, sy = p.origin_node.y;
      const len = p.length * Math.min(1.0, p.growth_progress);
      const ex = sx + len * Math.cos(p.direction), ey = sy + len * Math.sin(p.direction);
      const c = this.blend_colors(this.accent_color, this.secondary_color, p.confidence);
      g.line(c, [int(sx), int(sy)], [int(ex), int(ey)], 2);
      for (const br of p.branch_points) {
        if (!br.active || p.growth_progress < br.progress) continue;
        const bx = sx + br.progress * p.length * Math.cos(p.direction), by = sy + br.progress * p.length * Math.sin(p.direction);
        g.line(c, [int(bx), int(by)], [int(bx + br.length * Math.cos(br.angle)), int(by + br.length * Math.sin(br.angle))], 1);
      }
    }
  }

  render_nodes(g) {
    const b = g.blended();
    for (const n of this.all_nodes) {
      const pos = [int(n.x), int(n.y)];
      let c = n.active ? this.brighten_color(this.primary_color, 1 + n.activation_level) : this.primary_color;
      if (this.alert_mode && random() < this.alert_intensity) c = this.accent_color;
      if (n.glow_intensity > 0) b.circle([...c, int(n.glow_intensity * 100)], pos, int(n.current_size + n.glow_intensity * 10));
      const ns = Math.max(1, int(n.current_size));
      g.circle(c, pos, ns);
      if (n.active) g.circle(this.secondary_color, pos, Math.max(1, Math.floor(ns / 2)));
    }
  }

  render_core(g) {
    const cp = [int(this.center_x), int(this.center_y)];
    const core = int(15 * (1 + 0.3 * Math.sin(this.global_pulse)));
    const c = this.alert_mode ? this.blend_colors(this.primary_color, this.accent_color, this.alert_intensity) : this.primary_color;
    const glow = core + 10, b = g.blended(), x = g.ctx;
    // Python draws these circles on one SRCALPHA surface (each overwrites the last), then blits it once: so every
    // annulus keeps its own alpha. Drawn here as separate annuli.
    for (let r = glow; r > core; r -= 2) {
      const a = int(150 * (r - core) / (glow - core) * 0.3), inner = r - 2 > core ? r - 2 : 0;
      x.beginPath(); x.arc(cp[0], cp[1], r, 0, TAU);
      if (inner > 0) x.arc(cp[0], cp[1], inner, 0, TAU, true);
      x.fillStyle = b.col([...c, a]); x.fill('evenodd');
    }
    g.circle(c, cp, core);
    g.circle(this.secondary_color, cp, Math.floor(core / 2));
  }

  render_data_overlay(g) {
    const texts = [
      `NETWORK ACTIVITY: ${pct(this.network_activity_level)}`,
      `PREDICTION CONFIDENCE: ${pct(uniform(0.7, 0.95))}`,
      `DATA STREAMS: ${this.data_streams.filter(s => s.stream_active).length}`,
      `ALERT LEVEL: ${this.alert_mode ? 'HIGH' : 'NORMAL'}`,
    ];
    texts.forEach((t, i) => g.text(t, 10, 10 + i * 20, 16, this.alert_mode && i === 3 ? this.accent_color : this.secondary_color));
  }

  blend_colors(c1, c2, f) {
    f = Math.max(0, Math.min(1, f));
    return [0, 1, 2].map(i => int(c1[i] * (1 - f) + c2[i] * f));
  }

  brighten_color(c, f) {
    f = Math.max(1, f);
    return c.slice(0, 3).map(v => Math.min(255, int(v * f)));
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'num_rings') {
      const n = Math.max(3, Math.min(8, int(value)));
      if (n !== this.rings.length) { this.num_rings = n; this.build_network(); this.parameters[name] = n; }
    }
  }

  reset() {
    this.build_network();
    this.global_pulse = 0; this.network_breathing = 0; this.reorganization_timer = 0;
    this.alert_mode = false; this.alert_intensity = 0.0;
    for (const n of this.all_nodes) { n.active = false; n.activation_level = 0.0; n.glow_intensity = 0.0; }
  }

  info() { return { nodes: this.all_nodes.length, 'active streams': this.data_streams.filter(s => s.stream_active).length }; }
}
