// Port of the Boid class in plugins/musical_flock.py (Reynolds flocking with audio-modulated weights).
import { Vector2D } from './vector2d.js';
import { uniform } from '../pyrand.js';
import { get, pymod } from '../plugin_base.js';

export class FlockBoid {
  constructor(x, y) {
    this.acceleration = new Vector2D(0, 0);
    this.angle = uniform(0, 2 * Math.PI);
    this.velocity = new Vector2D(Math.cos(this.angle), Math.sin(this.angle));
    this.location = new Vector2D(x, y);
    this.r = 3.0; this.maxforce = 0.05;
    // set from the plugin's max_speed / neighbor_radius / separation_radius parameters
    this.base_maxspeed = 2.5; this.neighbor_dist = 50.0; this.desired_separation = 25.0; this.maxspeed = this.base_maxspeed;
    this.trail = []; this.max_trail_length = 15;
    this.color_hue = uniform(0, 360);
    this.energy = 0.0;
    this.separation_weight = 1.5; this.alignment_weight = 1.0; this.cohesion_weight = 1.0;
    this.beat_response = 0.0; this.frequency_influence = 0.0;
  }

  run(boids, f, bounds) {
    this.flock(boids, f);
    this.update();
    this.borders(bounds);
    this.update_audio_response(f);
    this.update_trail();
  }

  update_audio_response(f) {
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false);
    const frequency = get(f, 'dominant_frequency', 0);
    const fb = get(f, 'frequency_bands', { bass: 0, mid: 0, treble: 0 });
    this.energy += amplitude * 10;
    this.energy *= 0.95;
    if (beat) this.beat_response = Math.min(this.beat_response + amplitude * 5, 3.0);
    else this.beat_response *= 0.9;
    this.frequency_influence = frequency * 0.001;
    this.color_hue += this.frequency_influence + amplitude * 20;
    this.color_hue = pymod(this.color_hue, 360);
    this.separation_weight = 1.5 + (fb.bass ?? 0) * 2;
    this.alignment_weight = 1.0 + (fb.treble ?? 0) * 1.5;
    this.cohesion_weight = 1.0 + (fb.mid ?? 0) * 1.2;
    this.maxspeed = this.beat_response > 0 ? this.base_maxspeed + this.beat_response * 1.5 : this.base_maxspeed;
  }

  update_trail() {
    this.trail.push([this.location.x, this.location.y, this.color_hue]);
    if (this.trail.length > this.max_trail_length) this.trail.shift();
  }

  apply_force(force) { this.acceleration.add(force); }

  flock(boids, f) {
    const sep = this.separate(boids), ali = this.align(boids), coh = this.cohesion(boids);
    sep.mult(this.separation_weight); ali.mult(this.alignment_weight); coh.mult(this.cohesion_weight);
    this.apply_force(sep); this.apply_force(ali); this.apply_force(coh);
    const amplitude = get(f, 'amplitude', 0);
    if (amplitude > 0.5) {
      const rf = new Vector2D(uniform(-1, 1) * amplitude, uniform(-1, 1) * amplitude);
      rf.mult(0.02);
      this.apply_force(rf);
    }
  }

  update() {
    this.velocity.add(this.acceleration);
    this.velocity.limit(this.maxspeed);
    this.location.add(this.velocity);
    this.acceleration.mult(0);
  }

  seek(target) {
    const desired = Vector2D.sub_static(target, this.location);
    desired.normalize(); desired.mult(this.maxspeed);
    const steer = Vector2D.sub_static(desired, this.velocity);
    steer.limit(this.maxforce);
    return steer;
  }

  separate(boids) {
    const desired = this.desired_separation, steer = new Vector2D(0, 0);
    let count = 0;
    for (const o of boids) {
      const d = Vector2D.dist(this.location, o.location);
      if (d > 0 && d < desired) {
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
      const d = Vector2D.dist(this.location, o.location);
      if (d > 0 && d < this.neighbor_dist) { sum.add(o.velocity); count++; }
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
      const d = Vector2D.dist(this.location, o.location);
      if (d > 0 && d < this.neighbor_dist) { sum.add(o.location); count++; }
    }
    if (count > 0) { sum.div(count); return this.seek(sum); }
    return new Vector2D(0, 0);
  }

  borders([width, height]) {
    const L = this.location, r = this.r;
    if (L.x < -r) L.x = width + r;
    if (L.y < -r) L.y = height + r;
    if (L.x > width + r) L.x = -r;
    if (L.y > height + r) L.y = -r;
  }
}
