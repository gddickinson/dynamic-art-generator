// Port of plugins/digital_spectre.py (DigitalSpectrePlugin): dark AI monoliths rising from a white void, swirling
// smoke, a neural grid, scan lines and glitches. All drawing is opaque on the display surface, as in Python (alpha is
// simulated by mixing towards white).
import { ArtPlugin, get, bands, int } from '../plugin_base.js';
import { uniform, random, choice } from '../pyrand.js';
import { AIMonolith } from './spectre_parts.js';

// tuple(int(c + (255 - c) * (1 - a / full)) for c in color)
const toward = (c, a, full = 255) => c.map(v => int(v + (255 - v) * (1 - a / full)));

export class DigitalSpectrePlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Digital Spectre';
  static PLUGIN_DESCRIPTION = 'AI consciousness manifesting as dark geometric forms';
  static SOURCE = 'plugins/digital_spectre.py';

  constructor(size) {
    super(DigitalSpectrePlugin.PLUGIN_NAME, size);
    this.background_color = [245, 245, 245]; this.smoke_color = [20, 20, 20];
    this.monolith_color = [30, 30, 30]; this.scan_color = [60, 60, 60]; this.glitch_color = [0, 0, 0];
    this.monoliths = []; this.max_monoliths = 6; this.monolith_types = ['cube', 'pyramid', 'neural_node'];
    this.smoke_particles = []; this.max_smoke_particles = 800;
    this.scan_lines = []; this.neural_grid = []; this.data_streams = []; this.glitch_regions = [];
    this.audio_sensitivity = 1.2; this.bass_emergence_threshold = 0.3; this.beat_amplification = 2.5;
    this.frequency_scan_speed = 1.0;
    this.smoke_opacity = 0.7; this.monolith_opacity = 0.8; this.scan_intensity = 0.5;
    this.glitch_frequency = 0.02; this.neural_activity = 0.3;
    this.enable_smoke = true; this.enable_scanning = true; this.enable_glitches = true;
    this.enable_neural_grid = true; this.enable_data_streams = true;
    this.parameters = {
      max_monoliths: this.max_monoliths, max_smoke_particles: this.max_smoke_particles,
      audio_sensitivity: this.audio_sensitivity, beat_amplification: this.beat_amplification,
      smoke_opacity: this.smoke_opacity, monolith_opacity: this.monolith_opacity, scan_intensity: this.scan_intensity,
      glitch_frequency: this.glitch_frequency, neural_activity: this.neural_activity, enable_smoke: this.enable_smoke,
      enable_scanning: this.enable_scanning, enable_glitches: this.enable_glitches,
      enable_neural_grid: this.enable_neural_grid,
    };
    this.create_monoliths();
    this.create_neural_grid();
    this.time_offset = 0; this.global_scan_phase = 0; this.ai_consciousness_level = 0;
  }

  create_monoliths() {
    this.monoliths = [];
    const [W, H] = this.surface_size;
    for (let i = 0; i < int(this.max_monoliths); i++) {
      const x = W / (this.max_monoliths + 1) * (i + 1) + uniform(-50, 50);
      this.monoliths.push(new AIMonolith(x, H - 50, choice(this.monolith_types)));
    }
  }

  create_neural_grid() {
    this.neural_grid = [];
    const sp = 60, [W, H] = this.surface_size;
    for (let x = 0; x < W; x += sp) {
      for (let y = 0; y < H; y += sp) {
        this.neural_grid.push({ x: x + uniform(-10, 10), y: y + uniform(-10, 10), activity: uniform(0, 1), connections: [] });
      }
    }
    for (const node of this.neural_grid) {
      for (const other of this.neural_grid) {
        if (node === other) continue;
        const d = Math.hypot(node.x - other.x, node.y - other.y);
        if (d < sp * 1.5 && random() < 0.3) node.connections.push(other);
      }
    }
  }

  update(f, dt) {
    this.time_offset += dt;
    const amplitude = get(f, 'amplitude', 0) * this.audio_sensitivity;
    const beat = get(f, 'beat_detected', false), frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    const target = ((fb.bass ?? 0) + amplitude) * 0.5;
    this.ai_consciousness_level += (target - this.ai_consciousness_level) * dt * 2;
    this.global_scan_phase += frequency * 0.001 * this.frequency_scan_speed * dt + dt * 2;
    for (const m of this.monoliths) {
      m.update(dt, f);
      if (this.enable_smoke) {
        for (const e of m.smoke_emitters) {
          if (m.should_emit_smoke(e) && this.smoke_particles.length < this.max_smoke_particles) {
            this.smoke_particles.push(m.emit_smoke(e));
          }
        }
      }
    }
    if (this.enable_smoke) {
      const wx = Math.sin(this.time_offset * 0.5) * 10;
      let wy = -20 + Math.cos(this.time_offset * 0.3) * 5;
      if (beat) wy -= amplitude * 50 * this.beat_amplification;
      const forces = [wx, wy];
      this.smoke_particles = this.smoke_particles.filter(p => { p.update(dt, forces, this.surface_size); return p.is_alive(); });
    }
    if (this.enable_neural_grid) {
      const at = (fb.mid ?? 0) * 2 + amplitude * 0.5;
      for (const n of this.neural_grid) {
        n.activity += (at - n.activity) * dt * 3;
        n.activity = Math.max(0, Math.min(1, n.activity));
      }
    }
    if (this.enable_scanning) this.update_scan_lines(amplitude, frequency);
    if (this.enable_glitches && beat) this.create_glitch_region(amplitude);
  }

  update_scan_lines(amplitude, frequency) {
    const speed = 100 + frequency * 0.1 + amplitude * 50, [W, H] = this.surface_size;
    if (random() < 0.1 + amplitude * 0.2) {
      this.scan_lines.push({
        x: uniform(0, W), y: -10, speed, width: uniform(1, 3), intensity: amplitude * this.scan_intensity,
        type: choice(['vertical', 'horizontal', 'diagonal']),
      });
    }
    this.scan_lines = this.scan_lines.filter(s => {
      if (s.type === 'vertical') s.y += s.speed * 0.016;
      else if (s.type === 'horizontal') s.x += s.speed * 0.016;
      else { s.x += s.speed * 0.016 * 0.7; s.y += s.speed * 0.016 * 0.7; }
      return !(s.y > H + 10 || s.x > W + 10);
    });
  }

  create_glitch_region(amplitude) {
    const [W, H] = this.surface_size;
    this.glitch_regions.push({
      x: uniform(0, W), y: uniform(0, H), width: uniform(20, 100) * amplitude, height: uniform(10, 50) * amplitude,
      life: uniform(0.1, 0.3), intensity: amplitude * 2,
    });
  }

  render(g) {
    g.fill(this.background_color);
    if (this.enable_neural_grid) this.render_neural_grid(g);
    if (this.enable_scanning) this.render_scan_lines(g);
    this.render_monoliths(g);
    if (this.enable_smoke) this.render_smoke(g);
    if (this.enable_glitches) this.render_glitches(g);
  }

  render_neural_grid(g) {
    for (const n of this.neural_grid) {
      if (n.activity <= 0.1) continue;
      for (const o of n.connections) {
        if (o.activity > 0.1) {
          const a = int(Math.min(n.activity, o.activity) * 30);
          if (a > 5) g.line(toward(this.scan_color, a, 30), [int(n.x), int(n.y)], [int(o.x), int(o.y)], 1);
        }
      }
      const na = int(n.activity * 50);
      if (na > 10) g.circle(toward(this.scan_color, na, 50), [int(n.x), int(n.y)], 2);
    }
  }

  render_scan_lines(g) {
    const [W, H] = this.surface_size;
    for (const s of this.scan_lines) {
      const a = int(s.intensity * 255);
      if (a <= 5) continue;
      const c = toward(this.scan_color, a), w = int(s.width);
      if (s.type === 'vertical') g.line(c, [int(s.x), 0], [int(s.x), H], w);
      else if (s.type === 'horizontal') g.line(c, [0, int(s.y)], [W, int(s.y)], w);
      else g.line(c, [int(s.x), int(s.y)], [int(s.x + 100), int(s.y + 100)], w);
    }
  }

  render_monoliths(g) {
    for (const m of this.monoliths) {
      const v = m.get_vertices();
      if (v.length < 3) continue;
      const a = int(m.opacity * this.monolith_opacity);
      if (a > 5) {
        g.polygon(toward(this.monolith_color, a), v);
        g.polygon(this.glitch_color, v, v.length <= 4 ? 2 : 1);
      }
      if (m.edge_glow > 10) {
        const ga = int(Math.min(255, m.edge_glow));
        g.polygon(toward(this.glitch_color, ga), v, 3);
      }
    }
  }

  render_smoke(g) {
    for (const p of this.smoke_particles) {
      const a = int(p.get_alpha() * this.smoke_opacity);
      if (a <= 5) continue;
      const c = toward(this.smoke_color, a), pos = [int(p.x), int(p.y)], size = Math.max(1, int(p.size));
      g.circle(c, pos, size);
      if (size > 2) g.circle(c.map(v => int(v + (255 - v) * 0.7)), pos, size - 1);
    }
  }

  render_glitches(g) {
    this.glitch_regions = this.glitch_regions.filter(gl => {
      gl.life -= 0.016;
      if (gl.life <= 0) return false;
      const a = int(gl.intensity * gl.life * 100);
      if (a > 10) {
        g.rect(this.glitch_color, [int(gl.x), int(gl.y), int(gl.width), int(gl.height)]);
        for (let y = int(gl.y); y < int(gl.y + gl.height); y += 3) {
          g.line([200, 200, 200], [int(gl.x), y], [int(gl.x + gl.width), y], 1);
        }
      }
      return true;
    });
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'max_monoliths') {
      const n = Math.max(2, Math.min(15, int(value)));
      if (n !== this.monoliths.length) { this.max_monoliths = n; this.create_monoliths(); this.parameters[name] = n; }
    } else if (name === 'max_smoke_particles') {
      this.max_smoke_particles = Math.max(50, Math.min(2000, int(value)));
      this.parameters[name] = this.max_smoke_particles;
    } else if (['smoke_opacity', 'monolith_opacity', 'scan_intensity'].includes(name)) {
      this[name] = Math.max(0, Math.min(1, Number(value)));
      this.parameters[name] = this[name];
    }
  }

  reset() {
    this.smoke_particles = []; this.scan_lines = []; this.glitch_regions = [];
    this.create_monoliths();
    this.time_offset = 0; this.global_scan_phase = 0; this.ai_consciousness_level = 0;
  }

  info() { return { monoliths: this.monoliths.length, 'smoke particles': this.smoke_particles.length }; }
}
