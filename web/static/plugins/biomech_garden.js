// Port of plugins/biomech_garden.py (BioMechGardenPlugin): mechanical vines with gear joints, blooming gear-flowers,
// data packets on neural vines and a data network between nearby components.
import { ArtPlugin, hsvToRgb, get, bands, int } from '../plugin_base.js';
import { random, uniform, choice } from '../pyrand.js';
import { BioMechVine, GearFlower } from './biomech_parts.js';

// pygame raises "invalid color argument" for components outside 0..255; the Python code catches it and skips.
const valid = c => c.every(v => v >= 0 && v <= 255);

export class BioMechGardenPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Bio-Mechanical Garden';
  static PLUGIN_DESCRIPTION = 'Cyberpunk technology merging with organic plant growth';
  static SOURCE = 'plugins/biomech_garden.py';

  constructor(size) {
    super(BioMechGardenPlugin.PLUGIN_NAME, size);
    this.vines = []; this.flowers = []; this.data_streams = []; this.nutrient_pools = [];
    this.max_vines = 12; this.max_flowers = 8;
    this.vine_types = ['basic', 'cable', 'neural', 'fiber_optic'];
    this.background_color = [15, 25, 15]; this.soil_color = [40, 30, 20];
    this.metal_color = [120, 120, 130]; this.bio_glow_color = [0, 255, 100];
    this.audio_sensitivity = 1.0; this.growth_threshold = 0.3; this.bloom_sensitivity = 1.2; this.data_flow_rate = 1.0;
    this.ecosystem_energy = 0.5; this.nutrient_level = 1.0; this.data_network_activity = 0;
    this.enable_bio_glow = true; this.enable_data_flow = true;
    this.enable_servo_animation = true;
    this.parameters = {
      max_vines: this.max_vines, max_flowers: this.max_flowers, audio_sensitivity: this.audio_sensitivity,
      growth_threshold: this.growth_threshold, bloom_sensitivity: this.bloom_sensitivity,
      data_flow_rate: this.data_flow_rate, enable_bio_glow: this.enable_bio_glow,
      enable_data_flow: this.enable_data_flow,
      enable_servo_animation: this.enable_servo_animation,
    };
    this.plant_initial_seeds();
    this.time_offset = 0; this.last_growth_time = 0;
  }

  plant_initial_seeds() {
    const [W, H] = this.surface_size;
    for (let i = 0; i < 3; i++) {
      const x = uniform(50, W - 50), y = H - 30;
      this.vines.push(new BioMechVine(x, y, choice(this.vine_types)));
    }
    for (let i = 0; i < 2; i++) {
      const x = uniform(100, W - 100), y = uniform(200, H - 100);
      this.flowers.push(new GearFlower(x, y));
    }
  }

  update(f, dt) {
    this.time_offset += dt;
    const amplitude = get(f, 'amplitude', 0) * this.audio_sensitivity;
    const beat = get(f, 'beat_detected', false), fb = bands(f);
    const energyIn = (fb.bass ?? 0) + amplitude * 0.5;
    this.ecosystem_energy += (energyIn - this.ecosystem_energy) * dt * 2;
    this.data_network_activity = (fb.treble ?? 0) * this.data_flow_rate;
    if (this.vines.length < this.max_vines && amplitude > this.growth_threshold &&
        this.time_offset - this.last_growth_time > 2.0) {
      this.spawn_new_vine();
      this.last_growth_time = this.time_offset;
    }
    if (this.flowers.length < this.max_flowers && beat && amplitude > 0.5) this.spawn_new_flower();
    for (const vine of this.vines) {
      vine.update(dt, f || {}, this.surface_size);
      if (this.enable_data_flow && (vine.vine_type === 'neural' || vine.vine_type === 'fiber_optic') &&
          this.data_network_activity > 0.3 && random() < this.data_network_activity * dt) vine.add_data_packet(0);
    }
    const t = this.now();
    for (const flower of this.flowers) {
      const scaledBands = {};
      for (const [k, v] of Object.entries(fb)) scaledBands[k] = v * this.bloom_sensitivity;
      flower.update(dt, { ...(f || {}), frequency_bands: scaledBands }, t);
    }
    // Clean up small vines that can no longer grow (new vines start with one segment and grow over time)
    this.vines = this.vines.filter(v => v.segments.length > 2 || v.segments.length < v.max_length);
  }

  spawn_new_vine() {
    const [W, H] = this.surface_size;
    let x, y;
    if (this.vines.length && random() < 0.7) {
      const parent = choice(this.vines);
      const [px, py] = parent.segments[parent.segments.length - 1];
      x = px + uniform(-50, 50); y = py + uniform(-20, 20);
    } else {
      x = uniform(50, W - 50); y = uniform(H - 100, H - 30);
    }
    x = Math.max(50, Math.min(W - 50, x)); y = Math.max(50, Math.min(H - 30, y));
    this.vines.push(new BioMechVine(x, y, choice(this.vine_types)));
  }

  spawn_new_flower() {
    const [W, H] = this.surface_size;
    let x, y;
    if (this.vines.length) {
      const vine = choice(this.vines);
      const [vx, vy] = vine.segments[vine.segments.length - 1];
      x = vx + uniform(-30, 30); y = vy + uniform(-30, 30);
    } else {
      x = uniform(100, W - 100); y = uniform(200, H - 100);
    }
    x = Math.max(100, Math.min(W - 100, x)); y = Math.max(100, Math.min(H - 100, y));
    this.flowers.push(new GearFlower(x, y));
  }

  render(g) {
    const [W, H] = this.surface_size;
    g.fill(this.background_color);
    g.rect(this.soil_color, [0, H - 40, W, 40]);
    this.render_vines(g);
    this.render_flowers(g);
    if (this.enable_data_flow) this.render_data_network(g);
  }

  render_vines(g) {
    const b = g.blended();
    for (const vine of this.vines) {
      const s = vine.segments;
      if (s.length < 2) continue;
      for (let i = 1; i < s.length; i++) {
        const start = [int(s[i - 1][0]), int(s[i - 1][1])], end = [int(s[i][0]), int(s[i][1])];
        const color = vine.get_segment_color(i);
        const th = Math.max(1, int(vine.thickness));
        if (valid(color)) g.line(color, start, end, th);
        if (this.enable_bio_glow && vine.bio_luminescence > 0.1) {
          b.circle([...this.bio_glow_color, int(vine.bio_luminescence * 100)], end, th * 2);
        }
      }
      for (const gear of vine.gears) this.render_gear(g, gear, vine.energy_level);
      if (vine.vine_type === 'neural' || vine.vine_type === 'fiber_optic') {
        for (const packet of vine.data_flow) this.render_data_packet(g, vine, packet);
      }
    }
  }

  render_gear(g, gear, energy) {
    const pos = [int(gear.x), int(gear.y)], size = int(gear.size);
    const bb = 120 + int(energy * 100);
    const gc = [Math.min(255, bb), Math.min(255, bb), Math.min(255, bb + 20)];
    if (!valid(gc)) return;
    g.circle(gc, pos, size);
    for (let i = 0; i < 8; i++) {
      const a = (gear.rotation + (360 / 8) * i) * Math.PI / 180;
      g.line(gc, [int(pos[0] + (size - 2) * Math.cos(a)), int(pos[1] + (size - 2) * Math.sin(a))],
        [int(pos[0] + (size + 2) * Math.cos(a)), int(pos[1] + (size + 2) * Math.sin(a))], 2);
    }
    g.circle(gc.map(c => Math.min(255, c + 30)), pos, Math.max(1, Math.floor(size / 3)));
  }

  render_data_packet(g, vine, packet) {
    const s = vine.segments;
    if (packet.position >= s.length - 1) return;
    const idx = int(packet.position), prog = packet.position - idx;
    if (idx + 1 >= s.length) return;
    const x = s[idx][0] + (s[idx + 1][0] - s[idx][0]) * prog, y = s[idx][1] + (s[idx + 1][1] - s[idx][1]) * prog;
    const color = hsvToRgb(packet.color, 0.9, 1.0);
    const pos = [int(x), int(y)], size = Math.max(1, int(packet.size));
    g.circle(color, pos, size);
    g.blended().circle([...color, int(packet.intensity * 150)], pos, size * 2);
  }

  render_flowers(g) {
    for (const fl of this.flowers) {
      const pos = [int(fl.x), int(fl.y)];
      for (let i = 0; i < fl.petal_count; i++) {
        const a = ((360 / fl.petal_count) * i + (this.enable_servo_animation ? fl.servo_angle : 0)) * Math.PI / 180;
        const len = fl.petal_length * fl.bloom_state;
        const ex = fl.x + len * Math.cos(a), ey = fl.y + len * Math.sin(a);
        const pc = hsvToRgb(fl.hue, 0.8, 0.9), pf = 1 + fl.bio_pulse * 0.3;
        const ec = pc.map(c => Math.min(255, int(c * pf)));
        const end = [int(ex), int(ey)];
        g.line(ec, pos, end, Math.max(1, int(3 * fl.bloom_state)));
        g.circle(this.metal_color, end, Math.max(1, int(2 * fl.bloom_state)));
      }
      const cs = int(fl.center_size);
      g.circle(hsvToRgb(fl.hue, 0.6, 0.7), pos, cs);
      this.render_gear(g, { x: fl.x, y: fl.y, size: cs, rotation: fl.gear_rotation, type: 'gear' }, fl.bio_pulse);
    }
  }

  render_data_network(g) {
    if (this.data_network_activity < 0.2) return;
    const comps = this.flowers.map(f => [f.x, f.y]);
    for (const v of this.vines) {
      if (v.segments.length && (v.vine_type === 'neural' || v.vine_type === 'fiber_optic')) comps.push(v.segments[v.segments.length - 1]);
    }
    const b = g.blended();
    for (let i = 0; i < comps.length; i++) {
      for (let j = i + 1; j < comps.length; j++) {
        const c1 = comps[i], c2 = comps[j];
        const d = Math.hypot(c1[0] - c2[0], c1[1] - c2[1]);
        if (d >= 100) continue;
        const alpha = int((1 - d / 100) * this.data_network_activity * 100);
        if (alpha <= 10) continue;
        // Python draws the line on a (int(d)+20) x 20 surface from (10,10), rotates it and centres it on the
        // midpoint of the two components: a line of length int(d) through the midpoint along the connection.
        const ang = Math.atan2(c2[1] - c1[1], c2[0] - c1[0]), co = Math.cos(ang), si = Math.sin(ang);
        const ox = (c1[0] + c2[0]) / 2, oy = (c1[1] + c2[1]) / 2;
        const u2 = int(d) / 2, u1 = -u2;
        b.line([...this.bio_glow_color, alpha], [ox + u1 * co, oy + u1 * si], [ox + u2 * co, oy + u2 * si], 1);
      }
    }
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'max_vines') {
      this.max_vines = Math.max(2, Math.min(30, int(value))); this.parameters[name] = this.max_vines;
    } else if (name === 'max_flowers') {
      this.max_flowers = Math.max(1, Math.min(20, int(value))); this.parameters[name] = this.max_flowers;
    }
  }

  reset() {
    this.vines = []; this.flowers = []; this.data_streams = [];
    this.ecosystem_energy = 0.5; this.data_network_activity = 0; this.time_offset = 0; this.last_growth_time = 0;
    this.plant_initial_seeds();
  }

  info() {
    return { vines: this.vines.length, flowers: this.flowers.length,
      'bloomed flowers': this.flowers.filter(f => f.bloom_state > 0.5).length };
  }
}
