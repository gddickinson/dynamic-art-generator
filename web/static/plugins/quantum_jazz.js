// Port of plugins/quantum_jazz.py (QuantumJazzPlugin): particles in superposition that collapse on beats, with
// uncertainty clouds, entanglement, probability waves and a quantum-field grid.
import { ArtPlugin, get, bands, int } from '../plugin_base.js';
import { uniform, randint } from '../pyrand.js';
import { QuantumParticle, ProbabilityWave } from './quantum_jazz_parts.js';

export class QuantumJazzPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Quantum Jazz';
  static PLUGIN_DESCRIPTION = 'Quantum physics meets jazz improvisation';
  static SOURCE = 'plugins/quantum_jazz.py';

  constructor(size) {
    super(QuantumJazzPlugin.PLUGIN_NAME, size);
    this.particles = []; this.probability_waves = []; this.photons = []; this.entanglement_pairs = [];
    this.max_particles = 15; this.particle_creation_rate = 0.3; this.wave_creation_rate = 0.2;
    this.quantum_coherence_time = 5.0;
    this.improvisation_intensity = 0.7; this.rhythm_complexity = 1.0; this.harmonic_progression = 0; this.jazz_tempo = 120;
    this.background_color = [15, 15, 30]; this.jazz_gold = [255, 215, 0]; this.quantum_blue = [100, 150, 255];
    this.uncertainty_gray = [80, 80, 120]; this.entanglement_red = [255, 100, 100];
    this.audio_sensitivity = 1.2; this.beat_observation_strength = 2.0; this.frequency_quantum_coupling = 1.5;
    this.show_uncertainty = true; this.show_probability_waves = true; this.show_entanglement = true;
    this.show_particle_trails = true; this.enable_jazz_improvisation = true;
    this.parameters = {
      max_particles: this.max_particles, particle_creation_rate: this.particle_creation_rate,
      improvisation_intensity: this.improvisation_intensity, rhythm_complexity: this.rhythm_complexity,
      audio_sensitivity: this.audio_sensitivity, beat_observation_strength: this.beat_observation_strength,
      quantum_coherence_time: this.quantum_coherence_time, show_uncertainty: this.show_uncertainty,
      show_probability_waves: this.show_probability_waves, show_entanglement: this.show_entanglement,
      show_particle_trails: this.show_particle_trails, enable_jazz_improvisation: this.enable_jazz_improvisation,
    };
    this.create_initial_particles();
    this.time_offset = 0; this.last_creation_time = 0; this.quantum_field_energy = 0;
  }

  create_initial_particles() {
    for (let i = 0; i < 3; i++) {
      const x = uniform(100, this.surface_size[0] - 100), y = uniform(100, this.surface_size[1] - 100);
      this.particles.push(new QuantumParticle(x, y, randint(1, 3)));
    }
  }

  update(f, dt) {
    this.time_offset += dt;
    const amplitude = get(f, 'amplitude', 0) * this.audio_sensitivity, beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    const input = (fb.bass ?? 0) + amplitude * 0.5;
    this.quantum_field_energy += (input - this.quantum_field_energy) * dt * 3;
    this.harmonic_progression += dt * (this.jazz_tempo / 60) * this.rhythm_complexity;
    // A creation rate of 0 means no new pairs.
    if (this.particles.length < this.max_particles && this.quantum_field_energy > 0.5 &&
        this.particle_creation_rate > 0 && this.time_offset - this.last_creation_time > 1 / this.particle_creation_rate) {
      this.create_particle_pair();
      this.last_creation_time = this.time_offset;
    }
    if (beat && this.show_probability_waves) this.create_probability_wave(amplitude, frequency);
    for (const p of [...this.particles]) {
      if (this.enable_jazz_improvisation) p.improvisation_factor = this.improvisation_intensity;
      p.coherence_time = this.quantum_coherence_time; p.observation_strength = this.beat_observation_strength;
      p.update(dt, f, this.particles);
      if (p.x < -50 || p.x > this.surface_size[0] + 50 || p.y < -50 || p.y > this.surface_size[1] + 50) {
        this.particles.splice(this.particles.indexOf(p), 1);
      }
    }
    for (const w of [...this.probability_waves]) {
      w.update(dt, f);
      if (!w.is_alive()) this.probability_waves.splice(this.probability_waves.indexOf(w), 1);
    }
  }

  create_particle_pair() {
    const x = uniform(100, this.surface_size[0] - 100), y = uniform(100, this.surface_size[1] - 100);
    const e = randint(1, 4);
    const p = new QuantumParticle(x - 10, y, e), a = new QuantumParticle(x + 10, y, e);
    const ang = uniform(0, 2 * Math.PI);
    p.momentum_x = 30 * Math.cos(ang); p.momentum_y = 30 * Math.sin(ang);
    a.momentum_x = -p.momentum_x; a.momentum_y = -p.momentum_y;
    p.improvisation_factor = uniform(0.3, 1.0); a.improvisation_factor = 1.0 - p.improvisation_factor;
    this.particles.push(p, a);
  }

  create_probability_wave(amplitude, frequency) {
    const x = uniform(0, this.surface_size[0]), y = uniform(0, this.surface_size[1]);
    this.probability_waves.push(new ProbabilityWave(x, y, 50 + frequency * 0.1, amplitude * 0.5));
  }

  render(g) {
    g.fill(this.background_color);
    const b = g.blended();
    if (this.show_probability_waves) this.render_probability_waves(b);
    if (this.show_uncertainty) this.render_uncertainty_clouds(b);
    if (this.show_particle_trails) this.render_particle_trails(b);
    if (this.show_entanglement) this.render_entanglement(b);
    this.render_particles(g, b);
    this.render_quantum_field(b);
  }

  render_probability_waves(b) {
    for (const w of this.probability_waves) {
      if (w.amplitude < 0.05) continue;
      for (let i = 0; i < 5; i++) {
        const r = w.radius - i * (w.wavelength / 2);
        if (r > 0) {
          const alpha = int(w.amplitude * 100 * (1 - i / 5));
          if (alpha > 5) b.circle([...this.quantum_blue, alpha], [w.origin_x, w.origin_y], int(r), 2);
        }
      }
    }
  }

  render_uncertainty_clouds(b) {
    for (const p of this.particles) {
      if (!p.uncertainty_cloud.length) continue;
      const a = int(p.coherence * 60);
      if (a < 5) continue;
      const c = [...this.uncertainty_gray, a];
      for (const [x, y] of p.uncertainty_cloud) b.circle(c, [int(x), int(y)], 2);
    }
  }

  render_particle_trails(b) {
    const t = this.now();
    for (const p of this.particles) {
      if (p.trail.length < 2) continue;
      for (let i = 1; i < p.trail.length; i++) {
        const alpha = Math.max(0, int(255 * (1 - (t - p.trail[i][2]) / 2.0)));
        if (alpha > 10) {
          const s = [int(p.trail[i - 1][0]), int(p.trail[i - 1][1])], e = [int(p.trail[i][0]), int(p.trail[i][1])];
          b.line([...p.get_color(), alpha], s, e, 1);
        }
      }
    }
  }

  render_entanglement(b) {
    for (const p of this.particles) {
      if (!(p.entangled_partner && p.entanglement_strength > 0.1)) continue;
      const s = [int(p.x), int(p.y)], e = [int(p.entangled_partner.x), int(p.entangled_partner.y)];
      const alpha = int(p.entanglement_strength * 150);
      const d = Math.sqrt((e[0] - s[0]) ** 2 + (e[1] - s[1]) ** 2);
      if (d > 0) {
        // As in Python ("simple line for now"): the wavy points are computed there but unused; a horizontal line of
        // the partner distance is drawn from the pair's top-left corner.
        const ox = Math.min(s[0], e[0]) - 20, oy = Math.min(s[1], e[1]) - 20;
        b.line([...this.entanglement_red, alpha], [ox + 10, oy + 20], [ox + int(d) + 10, oy + 20], 2);
      }
    }
  }

  render_particles(g, b) {
    for (const p of this.particles) {
      const pos = [int(p.x), int(p.y)], color = p.get_color(), size = int(p.size);
      g.circle(color, pos, size);
      for (let lv = 0; lv < p.energy_level; lv++) {
        b.circle([...color, Math.max(20, 100 - lv * 20)], pos, size + lv * 3, 1);
      }
      if (p.observed) g.circle([255, 255, 255], pos, size + 2, 1);
      else for (let i = 0; i < 3; i++) b.circle([...color, 50 - i * 15], pos, size + i);
    }
  }

  render_quantum_field(b) {
    if (this.quantum_field_energy < 0.1) return;
    const a = int(this.quantum_field_energy * 30);
    if (a <= 5) return;
    const c = [...this.jazz_gold, a], [W, H] = this.surface_size;
    for (let x = 0; x < W; x += 40) b.line(c, [x + 1, 0], [x + 1, H], 1);
    for (let y = 0; y < H; y += 40) b.line(c, [0, y + 1], [W, y + 1], 1);
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'max_particles') {
      this.max_particles = Math.max(3, Math.min(50, int(value))); this.parameters[name] = this.max_particles;
    } else if (name === 'improvisation_intensity' || name === 'rhythm_complexity') {
      this[name] = Math.max(0.1, Math.min(2.0, Number(value))); this.parameters[name] = this[name];
    }
  }

  reset() {
    this.particles = []; this.probability_waves = []; this.photons = []; this.entanglement_pairs = [];
    this.time_offset = 0; this.last_creation_time = 0; this.quantum_field_energy = 0; this.harmonic_progression = 0;
    this.create_initial_particles();
  }

  info() {
    return { particles: this.particles.length, observed: this.particles.filter(p => p.observed).length, waves: this.probability_waves.length };
  }
}
