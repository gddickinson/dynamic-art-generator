// Helpers for quantum_jazz.js: generate_wave_function, QuantumParticle and ProbabilityWave from plugins/quantum_jazz.py.
import { hsvToRgb, now, int, pymod, get, bands } from '../plugin_base.js';
import { uniform, random, choice } from '../pyrand.js';

// np.random.random(size) + 1j * np.random.random(size), as [re, im] pairs.
export function generateWaveFunction(size) {
  const re = Array.from({ length: size }, random), im = Array.from({ length: size }, random);
  return re.map((r, i) => [r, im[i]]);
}

const BASE_HUES = [240, 200, 280, 320, 60];

export class QuantumParticle {
  constructor(x, y, energy_level = 1) {
    this.x = x; this.y = y;
    this.momentum_x = uniform(-50, 50); this.momentum_y = uniform(-50, 50);
    this.energy_level = energy_level;
    this.wave_function = generateWaveFunction(10);
    this.coherence = 1.0; this.observed = false; this.collapse_timer = 0;
    this.improvisation_factor = uniform(0.3, 1.0); this.rhythm_sync = uniform(0, 1);
    this.jazz_phrase_position = 0; this.spontaneity = uniform(0.5, 1.5);
    this.trail = []; this.uncertainty_cloud = [];
    this.color_phase = uniform(0, 2 * Math.PI);
    this.size = 3 + energy_level * 2;
    this.entangled_partner = null; this.entanglement_strength = 0;
  }

  update(dt, f, others) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    if (beat && !this.observed) this.observe_particle(amplitude);
    if (this.observed) {
      this.collapse_timer += dt;
      this.coherence = Math.max(0, 1 - this.collapse_timer * 0.5);
      if (this.coherence <= 0) this.reset_quantum_state();
    }
    const jazz = this.improvisation_factor * amplitude;
    if (frequency > 0) {
      const ne = 1 + pymod(int(frequency * 0.01), 5);
      if (ne !== this.energy_level) { this.energy_level = ne; this.emit_photon(); }
    }
    if (this.observed) this.update_classical_motion(dt, jazz);
    else this.update_quantum_motion(dt, jazz, fb);
    this.jazz_phrase_position += dt * (1 + jazz);
    if (random() < this.spontaneity * dt * 0.5) this.improvise_movement();
    this.update_uncertainty_cloud(dt);
    this.check_entanglement(others);
    this.trail.push([this.x, this.y, now()]);
    const t = now();
    this.trail = this.trail.filter(p => t - p[2] < 2.0);
    this.color_phase += dt * 3 + amplitude * 5;
  }

  observe_particle(intensity) {
    this.observed = true; this.collapse_timer = 0;
    const spread = 20 * (1 - intensity);
    this.x += uniform(-spread, spread); this.y += uniform(-spread, spread);
    const mi = intensity * 30;
    this.momentum_x += uniform(-mi, mi); this.momentum_y += uniform(-mi, mi);
  }

  reset_quantum_state() {
    this.observed = false; this.coherence = 1.0; this.collapse_timer = 0;
    this.wave_function = generateWaveFunction(10);
  }

  update_classical_motion(dt, jazz) {
    this.x += this.momentum_x * dt * (1 + jazz * 0.5);
    this.y += this.momentum_y * dt * (1 + jazz * 0.5);
    this.momentum_x *= 0.99; this.momentum_y *= 0.99;
  }

  update_quantum_motion(dt, jazz, fb) {
    const wa = 30 + jazz * 20, t = now();
    this.wave_function.forEach(([re, im], i) => {
      const phase = t * ((i + 1) * 0.5) + this.color_phase;
      this.x += re * wa * Math.sin(phase) * dt;
      this.y += im * wa * Math.cos(phase) * dt;
    });
    const orbit = (fb.bass ?? 0) * 40, of = 0.5 + (fb.mid ?? 0);
    this.x += orbit * Math.sin(t * of) * dt;
    this.y += orbit * Math.cos(t * of * 1.3) * dt;
  }

  improvise_movement() {
    const bx = (400 - this.x) * 0.1, by = (300 - this.y) * 0.1;   // Python assumes the 800x600 centre
    const ix = uniform(-30, 30), iy = uniform(-30, 30);
    this.momentum_x += bx + ix * this.improvisation_factor;
    this.momentum_y += by + iy * this.improvisation_factor;
  }

  update_uncertainty_cloud(_dt) {
    const us = this.observed ? 5 + this.collapse_timer * 10 : 15 + this.coherence * 20;
    this.uncertainty_cloud = [];
    const n = Math.max(3, int(us / 3));
    for (let i = 0; i < n; i++) {
      const a = uniform(0, 2 * Math.PI), d = uniform(0, us);
      this.uncertainty_cloud.push([this.x + d * Math.cos(a), this.y + d * Math.sin(a)]);
    }
  }

  check_entanglement(others) {
    if (this.entangled_partner) {
      const p = this.entangled_partner;
      const d = Math.sqrt((this.x - p.x) ** 2 + (this.y - p.y) ** 2);
      this.entanglement_strength = Math.max(0, 1 - d / 100);
      if (this.entanglement_strength < 0.1) this.break_entanglement();
    } else {
      for (const o of others) {
        if (o === this || o.entangled_partner) continue;
        const d = Math.sqrt((this.x - o.x) ** 2 + (this.y - o.y) ** 2);
        if (d < 50 && random() < 0.01) { this.create_entanglement(o); break; }
      }
    }
  }

  create_entanglement(o) {
    this.entangled_partner = o; o.entangled_partner = this;
    this.entanglement_strength = 1.0; o.entanglement_strength = 1.0;
  }

  break_entanglement() {
    if (this.entangled_partner) { this.entangled_partner.entangled_partner = null; this.entangled_partner.entanglement_strength = 0; }
    this.entangled_partner = null; this.entanglement_strength = 0;
  }

  emit_photon() {}

  get_color() {
    const base = this.energy_level <= 5 ? BASE_HUES[this.energy_level - 1] : 240;
    const shift = Math.sin(this.jazz_phrase_position) * 30;
    const hue = pymod(base + shift + this.color_phase * 180 / Math.PI, 360);
    return hsvToRgb(hue, 0.7 + this.coherence * 0.3, 0.6 + (this.observed ? 0.4 : 0.2));
  }
}

export class ProbabilityWave {
  constructor(x, y, wavelength, amplitude) {
    this.origin_x = x; this.origin_y = y; this.wavelength = wavelength; this.amplitude = amplitude;
    this.phase = 0; this.radius = 0; this.max_radius = 200; this.decay_rate = 0.5;
    this.rhythm_pattern = choice([1, 1.5, 2, 0.75]);
    this.improvisation_phase = uniform(0, 2 * Math.PI);
  }

  update(dt, f) {
    const amplitude = get(f, 'amplitude', 0), frequency = get(f, 'dominant_frequency', 0);
    this.radius += 60 * dt * (1 + amplitude * 0.5);
    this.phase += dt * this.rhythm_pattern * 5;
    this.wavelength *= (1 + frequency * 0.001) ** (dt * 0.1);
    this.amplitude *= (1 - this.decay_rate * dt);
  }

  is_alive() { return this.radius < this.max_radius && this.amplitude > 0.01; }

  get_amplitude_at(x, y) {
    const d = Math.sqrt((x - this.origin_x) ** 2 + (y - this.origin_y) ** 2);
    if (d === 0) return this.amplitude;
    return this.amplitude * Math.sin(2 * Math.PI * d / this.wavelength + this.phase) / (1 + d * 0.01);
  }
}
