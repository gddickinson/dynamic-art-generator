// Port of the prey Boid and the Predator classes in plugins/ecosystem.py.
import { Vector2D } from './vector2d.js';
import { uniform, random } from '../pyrand.js';
import { get, pymod, now } from '../plugin_base.js';

const BANDS0 = { bass: 0, mid: 0, treble: 0 };

function wrap(L, r, [width, height]) {
  if (L.x < -r) L.x = width + r;
  if (L.y < -r) L.y = height + r;
  if (L.x > width + r) L.x = -r;
  if (L.y > height + r) L.y = -r;
}

// Prey boid: flocks, flees predators, ages, reproduces.
export class PreyBoid {
  constructor(x, y) {
    this.acceleration = new Vector2D(0, 0);
    const angle = uniform(0, 2 * Math.PI);
    this.velocity = new Vector2D(Math.cos(angle), Math.sin(angle));
    this.location = new Vector2D(x, y);
    this.r = 3.0; this.maxspeed = 3.0; this.maxforce = 0.08;
    this.age = 0.0; this.max_age = uniform(15, 25); this.reproduction_age = uniform(3, 5);
    this.energy = 1.0; this.is_alive = true;
    this.trail = []; this.max_trail_length = 12;
    this.color_hue = uniform(60, 120); this.birth_flash = 0.0;
    this.separation_weight = 1.8; this.alignment_weight = 1.2; this.cohesion_weight = 1.0; this.flee_weight = 4.0;
    this.panic_level = 0.0; this.reproduction_urge = 0.0; this.last_reproduction = 0;
  }

  update(dt, all, predators, f, bounds) {
    const offspring = [];
    if (!this.is_alive) return offspring;
    this.age += dt;
    this.energy -= 0.02 * dt;
    if (this.age > this.max_age || this.energy <= 0) { this.is_alive = false; return offspring; }
    this.flock_and_flee(all, predators, f);
    this.update_physics();
    wrap(this.location, this.r, bounds);
    this.update_audio_response(f);
    this.update_trail();
    if (this.can_reproduce(f)) { const baby = this.reproduce(); if (baby) offspring.push(baby); }
    this.birth_flash *= 0.95;
    this.panic_level *= 0.92;
    return offspring;
  }

  flock_and_flee(all, predators, f) {
    const sep = this.separate(all), ali = this.align(all), coh = this.cohesion(all);
    const flee = this.flee_from_predators(predators);
    const fb = get(f, 'frequency_bands', BANDS0);
    const bassPanic = (fb.bass ?? 0) * 2, trebleCalm = fb.treble ?? 0;
    sep.mult(this.separation_weight + bassPanic);
    ali.mult(this.alignment_weight + trebleCalm * 0.5);
    coh.mult(this.cohesion_weight + trebleCalm);
    flee.mult(this.flee_weight);
    this.acceleration.add(sep); this.acceleration.add(ali); this.acceleration.add(coh); this.acceleration.add(flee);
    if (get(f, 'beat_detected', false)) {
      const amp = get(f, 'amplitude', 0);
      const pf = new Vector2D(uniform(-1, 1) * amp, uniform(-1, 1) * amp);
      pf.mult(0.15);
      this.acceleration.add(pf);
    }
  }

  flee_from_predators(predators) {
    const steer = new Vector2D(0, 0), R = 80;
    for (const p of predators) {
      const d = Vector2D.dist(this.location, p.location);
      if (d < R && d > 0) {
        const dir = Vector2D.sub_static(this.location, p.location);
        dir.normalize();
        const s = (R - d) / R;
        dir.mult(s * 2);
        steer.add(dir);
        this.panic_level = Math.min(this.panic_level + s * 2, 3.0);
      }
    }
    if (steer.mag() > 0) { steer.normalize(); steer.mult(this.maxspeed); steer.sub(this.velocity); steer.limit(this.maxforce * 2); }
    return steer;
  }

  can_reproduce(f) {
    if (this.age < this.reproduction_age || this.energy < 0.6 || this.panic_level > 1.0
        || now() - this.last_reproduction < 2.0) return false;
    const amp = get(f, 'amplitude', 0), fb = get(f, 'frequency_bands', BANDS0);
    this.reproduction_urge += (fb.mid ?? 0) * 0.5;
    if (get(f, 'beat_detected', false) && amp > 0.3) this.reproduction_urge += amp;
    return this.reproduction_urge > uniform(1.5, 2.5);
  }

  reproduce() {
    this.reproduction_urge = 0;
    this.last_reproduction = now();
    this.energy -= 0.3;
    const ox = uniform(-20, 20), oy = uniform(-20, 20);
    const baby = new PreyBoid(this.location.x + ox, this.location.y + oy);
    baby.color_hue = this.color_hue + uniform(-20, 20);
    baby.birth_flash = 2.0;
    return baby;
  }

  separate(boids) {
    const steer = new Vector2D(0, 0);
    let count = 0;
    for (const o of boids) {
      if (!o.is_alive || o === this) continue;
      const d = Vector2D.dist(this.location, o.location);
      if (d > 0 && d < 25.0) {
        const diff = Vector2D.sub_static(this.location, o.location);
        diff.normalize(); diff.div(d); steer.add(diff); count++;
      }
    }
    if (count > 0) {
      steer.div(count);
      if (steer.mag() > 0) { steer.normalize(); steer.mult(this.maxspeed); steer.sub(this.velocity); steer.limit(this.maxforce); }
    }
    return steer;
  }

  align(boids) {
    const sum = new Vector2D(0, 0);
    let count = 0;
    for (const o of boids) {
      if (!o.is_alive || o === this) continue;
      const d = Vector2D.dist(this.location, o.location);
      if (d > 0 && d < 50) { sum.add(o.velocity); count++; }
    }
    if (count > 0) {
      sum.div(count); sum.normalize(); sum.mult(this.maxspeed);
      const steer = Vector2D.sub_static(sum, this.velocity);
      steer.limit(this.maxforce);
      return steer;
    }
    return new Vector2D(0, 0);
  }

  cohesion(boids) {
    const sum = new Vector2D(0, 0);
    let count = 0;
    for (const o of boids) {
      if (!o.is_alive || o === this) continue;
      const d = Vector2D.dist(this.location, o.location);
      if (d > 0 && d < 50) { sum.add(o.location); count++; }
    }
    if (count > 0) { sum.div(count); return this.seek(sum); }
    return new Vector2D(0, 0);
  }

  seek(target) {
    const desired = Vector2D.sub_static(target, this.location);
    desired.normalize(); desired.mult(this.maxspeed);
    const steer = Vector2D.sub_static(desired, this.velocity);
    steer.limit(this.maxforce);
    return steer;
  }

  update_physics() {
    this.velocity.add(this.acceleration);
    this.velocity.limit(this.maxspeed * (1 + this.panic_level * 0.5));
    this.location.add(this.velocity);
    this.acceleration.mult(0);
  }

  update_audio_response(f) {
    const amp = get(f, 'amplitude', 0), freq = get(f, 'dominant_frequency', 0);
    const ageFactor = this.age / this.max_age;
    this.color_hue += freq * 0.002 + amp * 10;
    // As in Python, the next line overwrites the audio shift: the hue follows age only.
    this.color_hue = pymod(60 + ageFactor * 60, 360);
  }

  update_trail() {
    this.trail.push([this.location.x, this.location.y, this.color_hue]);
    if (this.trail.length > this.max_trail_length) this.trail.shift();
  }
}

// Predator: hunts the nearest prey within hunt_radius, gains energy from kills, starves otherwise.
export class Predator {
  constructor(x, y) {
    this.location = new Vector2D(x, y); this.velocity = new Vector2D(0, 0); this.acceleration = new Vector2D(0, 0);
    this.r = 8.0; this.maxspeed = 2.0; this.maxforce = 0.12;
    this.energy = 50.0; this.max_energy = 100.0; this.hunger = 0.0; this.hunt_radius = 120.0; this.kill_radius = 6.0;
    this.aggression = 1.0;   // the plugin's predator_aggression_multiplier
    this.color_hue = uniform(0, 30); this.trail = []; this.max_trail_length = 20;
    this.kill_flash = 0.0; this.size_pulse = 0.0; this.hunt_intensity = 0.0; this.beat_boost = 0.0;
    this.target = null; this.kills = 0;
  }

  update(dt, boids, f, bounds) {
    this.energy -= 8 * dt;
    this.hunger += dt;
    if (this.energy <= 0) { this.energy = 0; return 0; }
    this.hunt(boids, f);
    const kills = this.check_for_kills(boids);
    this.velocity.add(this.acceleration);
    this.velocity.limit(this.maxspeed * (1 + this.beat_boost * 0.4));
    this.location.add(this.velocity);
    this.acceleration.mult(0);
    wrap(this.location, this.r, bounds);
    this.update_audio_response(f);
    this.trail.push([this.location.x, this.location.y, this.color_hue]);
    if (this.trail.length > this.max_trail_length) this.trail.shift();
    this.kill_flash *= 0.9; this.beat_boost *= 0.95; this.hunt_intensity *= 0.98;
    return kills;
  }

  hunt(boids, f) {
    let closest = null, best = Infinity;
    for (const b of boids) {
      if (!b.is_alive) continue;
      const d = Vector2D.dist(this.location, b.location);
      if (d < this.hunt_radius && d < best) { best = d; closest = b; }
    }
    if (closest) {
      this.target = closest;
      const force = this.seek(closest.location);
      const amp = get(f, 'amplitude', 0), fb = get(f, 'frequency_bands', BANDS0);
      this.hunt_intensity += (fb.bass ?? 0) * 2;
      if (get(f, 'beat_detected', false)) this.beat_boost = Math.min(this.beat_boost + amp * 3, 5.0);
      force.mult((1 + this.hunt_intensity * 0.5 + this.hunger * 0.3) * this.aggression);
      this.acceleration.add(force);
    } else if (random() < 0.01) {
      const rf = new Vector2D(uniform(-1, 1), uniform(-1, 1));
      rf.mult(0.05);
      this.acceleration.add(rf);
    }
  }

  check_for_kills(boids) {
    let kills = 0;
    for (const b of boids) {
      if (!b.is_alive) continue;
      if (Vector2D.dist(this.location, b.location) < this.kill_radius) {
        b.is_alive = false; kills++; this.kills++;
        this.energy = Math.min(this.energy + 25, this.max_energy);
        this.hunger = Math.max(0, this.hunger - 1.5);
        this.kill_flash = 3.0; this.size_pulse = 2.0;
      }
    }
    return kills;
  }

  seek(target) {
    const desired = Vector2D.sub_static(target, this.location);
    const distance = desired.mag();   // measured before normalising: sprint when close
    desired.normalize();
    let speed = distance < 30 ? this.maxspeed * 2 : this.maxspeed;
    speed *= 1 + this.beat_boost * 0.3;
    desired.mult(speed);
    const steer = Vector2D.sub_static(desired, this.velocity);
    steer.limit(this.maxforce * (1 + this.hunt_intensity * 0.5));
    return steer;
  }

  update_audio_response(f) {
    const amp = get(f, 'amplitude', 0), freq = get(f, 'dominant_frequency', 0);
    const killFactor = Math.min(this.kills * 0.1, 1.0);
    this.color_hue = pymod(freq * 0.003 + amp * 15 + killFactor * 20, 360);
    this.size_pulse = Math.min(this.size_pulse + amp * 0.5, 3.0) * 0.95;
  }
}
