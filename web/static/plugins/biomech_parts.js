// Port of the helper classes in plugins/biomech_garden.py: BioMechVine (a growing part-organic, part-mechanical
// vine) and GearFlower (a mechanical flower that blooms and closes).
import { hsvToRgb, get, bands, int, pymod } from '../plugin_base.js';
import { random, uniform, randint, choice } from '../pyrand.js';

export class BioMechVine {
  constructor(x, y, vineType = 'basic') {
    this.segments = [[x, y]];
    this.growth_direction = uniform(-Math.PI / 4, Math.PI / 4) - Math.PI / 2;  // generally upward
    this.growth_speed = uniform(15, 30);
    this.max_length = randint(8, 25);
    this.thickness = uniform(2, 6);
    this.vine_type = vineType;   // basic, cable, neural, fiber_optic
    this.gears = []; this.joints = []; this.data_flow = []; this.energy_level = 0;
    this.bio_luminescence = 0; this.growth_energy = 1.0; this.nutrients = 1.0;
    this.color_hue = uniform(0, 360);
    this.pulse_phase = uniform(0, 2 * Math.PI);
    this.add_gear_joint(x, y);
  }

  add_gear_joint(x, y) {
    this.gears.push({ x, y, size: uniform(5, 12), rotation: 0, speed: uniform(0.5, 2.0),
      type: choice(['gear', 'servo', 'connector']) });
    this.joints.push({ x, y, angle: this.growth_direction, flexibility: uniform(0.1, 0.3) });
  }

  update(dt, f, bounds) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0), fb = bands(f);
    this.growth_energy += (fb.mid ?? 0) * dt * 2;
    this.growth_energy = Math.min(2.0, this.growth_energy);
    if (beat) this.bio_luminescence = Math.min(this.bio_luminescence + amplitude * 3, 2.0);
    else this.bio_luminescence *= 0.95;
    this.energy_level = amplitude + (fb.treble ?? 0);
    if (this.segments.length < this.max_length && this.growth_energy > 0.5) {
      const growthRate = this.growth_speed * this.growth_energy * dt;
      if (random() < growthRate * 0.1) {
        const [lx, ly] = this.segments[this.segments.length - 1];
        this.growth_direction += uniform(-0.3, 0.3);
        if (frequency > 0) this.growth_direction += Math.sin(frequency * 0.01) * 0.2;
        const nx = lx + Math.cos(this.growth_direction) * 10, ny = ly + Math.sin(this.growth_direction) * 10;
        if (nx > 10 && nx < bounds[0] - 10 && ny > 10 && ny < bounds[1] - 10) {
          this.segments.push([nx, ny]);
          if (this.segments.length % 3 === 0) this.add_gear_joint(nx, ny);
          if (this.vine_type === 'neural' || this.vine_type === 'fiber_optic') this.add_data_packet(0);
        }
      }
    }
    for (const gear of this.gears) {
      gear.rotation += gear.speed * this.energy_level * dt * 100;
      gear.rotation = pymod(gear.rotation, 360);
    }
    for (const packet of this.data_flow.slice()) {
      packet.position += packet.speed * dt;
      if (packet.position > this.segments.length - 1) this.data_flow.splice(this.data_flow.indexOf(packet), 1);
    }
    this.color_hue += frequency * 0.001 * dt + dt * 10;
    this.color_hue = pymod(this.color_hue, 360);
    this.pulse_phase += dt * 3 + amplitude * 5;
  }

  add_data_packet(start) {
    this.data_flow.push({ position: start, speed: uniform(2, 5), size: uniform(2, 4), color: uniform(0, 360),
      intensity: uniform(0.5, 1.0) });
  }

  // May return components above 255 (gear-joint segments under strong bio-luminescence), as in Python, where
  // pygame then rejects the colour and that segment is skipped.
  get_segment_color(i) {
    const base = hsvToRgb(this.color_hue, 0.7, 0.8);
    const bio = 1 + this.bio_luminescence * 0.5;
    if (i % 3 === 0) {
      const m = 0.5;
      return base.map(c => int(c * bio * m + 128 * (1 - m)));
    }
    return base.map(c => Math.min(255, int(c * bio)));
  }
}

export class GearFlower {
  constructor(x, y) {
    this.x = x; this.y = y;
    this.bloom_state = 0; this.target_bloom = 0;
    this.petal_count = randint(5, 8);
    this.center_size = uniform(8, 15);
    this.petal_length = uniform(15, 25);
    this.gear_rotation = 0; this.gear_speed = uniform(0.5, 1.5); this.servo_angle = 0;
    this.bio_pulse = 0; this.nectar_level = 0;
    this.hue = uniform(0, 360);
    this.bloom_timer = uniform(0, 5);
  }

  update(dt, f, now) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false), fb = bands(f);
    const trigger = (fb.mid ?? 0) + amplitude * 0.5;
    this.bloom_timer += dt;
    const auto = 0.5 + 0.5 * Math.sin(this.bloom_timer * 0.3);
    this.target_bloom = Math.max(trigger, auto * 0.3);
    const speed = 2.0;
    if (this.target_bloom > this.bloom_state) this.bloom_state += speed * dt;
    else this.bloom_state -= speed * dt * 0.5;
    this.bloom_state = Math.max(0, Math.min(1, this.bloom_state));
    this.gear_rotation += this.gear_speed * dt * 50;
    this.gear_rotation = pymod(this.gear_rotation, 360);
    this.servo_angle = Math.sin(now * 2) * 45 * this.bloom_state;
    if (beat) this.bio_pulse = Math.min(this.bio_pulse + amplitude * 2, 1.5);
    else this.bio_pulse *= 0.9;
    this.nectar_level = (fb.bass ?? 0) * this.bloom_state;
    this.hue += dt * 20;
    this.hue = pymod(this.hue, 360);
  }
}
