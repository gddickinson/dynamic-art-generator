// Registry of the JavaScript plugin ports: [Python PLUGIN_NAME, module file, exported class]. Same order as the
// API catalogue (the desktop default plugin first, then alphabetical). Modules load on demand.
export const REGISTRY = [
  ['Pendulum', 'pendulum.js', 'PendulumPlugin'],
  ['Bio-Mechanical Garden', 'biomech_garden.js', 'BioMechGardenPlugin'],
  ['Cosmic Web', 'cosmic_web.js', 'CosmicWebPlugin'],
  ['Digital Spectre', 'digital_spectre.js', 'DigitalSpectrePlugin'],
  ['Musical Ecosystem', 'ecosystem.js', 'MusicalEcosystemPlugin'],
  ['Musical Flock', 'musical_flock.js', 'MusicalFlockPlugin'],
  ['Neural Flow', 'neural_flow.js', 'NeuralFlowPlugin'],
  ['Noise Sphere', 'noise_sphere.js', 'NoiseSpherePlugin'],
  ['Particle Fountain', 'particle_fountain.js', 'ParticleFountainPlugin'],
  ['Particles', 'particles.js', 'ParticlePlugin'],
  ['Quantum Jazz', 'quantum_jazz.js', 'QuantumJazzPlugin'],
  ['Rehoboam', 'rehoboam.js', 'RehoboamPlugin'],
  ['Space Junk', 'space_junk.js', 'SpaceJunkPlugin'],
];

const cache = new Map();
// The plugin class for a Python plugin name.
export async function pluginClass(name) {
  const row = REGISTRY.find(r => r[0] === name);
  if (!row) throw new Error(`No JavaScript port of plugin "${name}"`);
  if (!cache.has(name)) cache.set(name, import(`./${row[1]}`).then(m => m[row[2]]));
  return cache.get(name);
}
