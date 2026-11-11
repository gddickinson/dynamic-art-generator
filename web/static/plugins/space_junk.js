// Port of plugins/space_junk.py (SpaceJunkPlugin): a field of rotating 3D cubes (after Ira Greenberg's "Space Junk").
import { ArtPlugin, get, bands, int } from '../plugin_base.js';
import { uniform, randint } from '../pyrand.js';
import { Vector3D, Cube3D } from './space_junk_cube.js';

export class SpaceJunkPlugin extends ArtPlugin {
  static PLUGIN_NAME = 'Space Junk';
  static PLUGIN_DESCRIPTION = '3D rotating cubes floating in audio-responsive space';
  static SOURCE = 'plugins/space_junk.py';

  constructor(size) {
    super(SpaceJunkPlugin.PLUGIN_NAME, size);
    this.cubes = []; this.cube_count = 150;
    this.global_rotation = new Vector3D(0, 0, 0);
    this.zoom = -200; this.fov = 500;
    this.audio_sensitivity = 1.0; this.rotation_speed = 1.0; this.zoom_sensitivity = 1.0; this.beat_zoom_boost = 0;
    this.ambient_light = 0.7;
    this.light_positions = [new Vector3D(65, 60, 100), new Vector3D(-65, -60, -150)];
    this.light_colors = [[51, 102, 255], [200, 40, 60]];
    this.enable_depth_sorting = true; this.enable_lighting = true; this.enable_trails = false; this.trail_alpha = 0.1;
    this.cube_size_range = [5, 15]; this.position_range = 140;
    this.parameters = {
      cube_count: this.cube_count, audio_sensitivity: this.audio_sensitivity, rotation_speed: this.rotation_speed,
      zoom_sensitivity: this.zoom_sensitivity, ambient_light: this.ambient_light,
      enable_depth_sorting: this.enable_depth_sorting, enable_lighting: this.enable_lighting,
      enable_trails: this.enable_trails, position_range: this.position_range,
    };
    this.createCubes();
    this.time_offset = 0;
    this.last_surface = null;
  }

  newCube() {
    const s = uniform(this.cube_size_range[0], this.cube_size_range[1]);
    const w = uniform(s * 0.8, s * 1.2), h = uniform(s * 0.8, s * 1.2), d = uniform(s * 0.8, s * 1.2);
    const r = this.position_range;
    const x = uniform(-r, r), y = uniform(-r, r), z = uniform(-r, r);
    return new Cube3D(w, h, d, x, y, z);
  }

  createCubes() {
    this.cubes = [];
    for (let i = 0; i < int(this.cube_count); i++) this.cubes.push(this.newCube());
  }

  update(f, dt) {
    this.time_offset += dt;
    const amplitude = get(f, 'amplitude', 0), beat = get(f, 'beat_detected', false), fb = bands(f);
    const base = this.rotation_speed * 20 * dt, rad = Math.PI / 180;   // degrees; rotate_* takes radians
    this.global_rotation.y += (base + (fb.bass ?? 0) * 30 * dt) * rad;
    this.global_rotation.x += (base * 0.7 + (fb.treble ?? 0) * 20 * dt) * rad;
    if (beat) this.beat_zoom_boost = amplitude * 100 * this.zoom_sensitivity;
    else this.beat_zoom_boost *= 0.9;
    const target = -200 + amplitude * 200 * this.zoom_sensitivity + this.beat_zoom_boost;
    this.zoom += (target - this.zoom) * dt * 2;
    for (const c of this.cubes) c.update(dt, f, this.global_rotation);
    if (beat && amplitude > 0.5 && this.cubes.length) {
      const idx = randint(0, this.cubes.length - 1);
      this.cubes[idx] = this.newCube();
    }
  }

  render(g) {
    const [W, H] = this.surface_size;
    if (this.enable_trails && this.last_surface) {
      // Python: blit the previous frame, then a black SRCALPHA layer filled with alpha 255*trail_alpha.
      g.blit(this.last_surface, 0, 0);
      g.blended().rect([0, 0, 0, int(255 * this.trail_alpha)], [0, 0, W, H]);
    }
    const data = this.cubes.map(c => {
      const vs = c.getTransformedVertices(this.global_rotation);
      for (const v of vs) v.z += this.zoom;
      return [c, vs, vs.reduce((s, v) => s + v.z, 0) / vs.length];
    });
    if (this.enable_depth_sorting) data.sort((a, b) => b[2] - a[2]);
    for (const [c, vs] of data) this.renderCube(g, c, vs);
    if (this.enable_trails) {
      this.last_surface ||= g.layer(W, H);
      this.last_surface.clear();
      this.last_surface.ctx.drawImage(g.canvas, 0, 0);
    }
  }

  renderCube(g, cube, vs) {
    const proj = [];
    for (const v of vs) {
      const p = v.project(this.surface_size[0], this.surface_size[1], this.fov);
      if (!p) return;   // Python: ZeroDivisionError caught, cube skipped
      proj.push(p[0]);
    }
    let lighting = this.ambient_light;
    if (this.enable_lighting) lighting += Math.max(0, 1.0 - Math.abs(vs[0].z) / 500);
    const faces = [];
    cube.faces.forEach((fi, idx) => {
      const z = fi.reduce((s, i) => s + vs[i].z, 0) / fi.length;
      if (z > -50) faces.push([idx, fi.map(i => proj[i]), z]);
    });
    faces.sort((a, b) => b[2] - a[2]);
    for (const [idx, pts] of faces) {
      g.polygon(cube.getFaceColor(idx, lighting), pts);
      if (cube.energy > 5) g.polygon([255, 255, 255], pts, 1);
    }
  }

  setParameter(name, value) {
    if (!(name in this.parameters)) return;
    this.parameters[name] = value;
    if (name in this) this[name] = value;
    if (name === 'cube_count') {
      const nc = Math.max(10, Math.min(500, int(value)));
      if (nc !== this.cubes.length) { this.cube_count = nc; this.createCubes(); this.parameters[name] = nc; }
    } else if (name === 'position_range') {
      this.position_range = Math.max(50, Math.min(300, Number(value))); this.parameters[name] = this.position_range;
    } else if (name === 'ambient_light') {
      this.ambient_light = Math.max(0, Math.min(2, Number(value))); this.parameters[name] = this.ambient_light;
    }
  }

  reset() {
    this.global_rotation = new Vector3D(0, 0, 0);
    this.zoom = -200; this.beat_zoom_boost = 0;
    this.createCubes();
    this.time_offset = 0; this.last_surface = null;
  }

  info() { return { cubes: this.cubes.length }; }
}
