"""Regression: the last plugin parameters that had no effect.

Wired (the parameter now changes behaviour; the default keeps the old behaviour except quantum_coherence_time, whose
documented default of 5 s replaces a hard-coded 2 s):
  Cosmic Web beat_amplification, Particle Fountain turbulence, Quantum Jazz quantum_coherence_time and
  beat_observation_strength, Noise Sphere beat_sensitivity.
Removed (nothing in the plugin they could control): Cosmic Web color_variance, Bio-Mechanical Garden
enable_particle_effects, Particle Fountain fade_trails.
"""
import random

from plugin_test_utils import LOUD, make

from plugins.biomech_garden import BioMechGardenPlugin
from plugins.cosmic_web import CosmicWebPlugin
from plugins.noise_sphere import NoiseSpherePlugin
from plugins.particle_fountain import ParticleFountainPlugin
from plugins.quantum_jazz import QuantumJazzPlugin, QuantumParticle


def test_dead_parameters_removed():
    assert "color_variance" not in make(CosmicWebPlugin).get_parameters()
    assert "enable_particle_effects" not in make(BioMechGardenPlugin).get_parameters()
    assert "fade_trails" not in make(ParticleFountainPlugin).get_parameters()


def _orb_energy(beat_amp):
    random.seed(1)
    p = make(CosmicWebPlugin)
    p.set_parameter("beat_amplification", beat_amp)
    p.update(LOUD, 1 / 60)
    return sum(o.energy for o in p.orbs)


def test_cosmic_beat_amplification():
    assert _orb_energy(6.0) > 1.5 * _orb_energy(3.0)


def _spread(turb):
    random.seed(2)
    p = make(ParticleFountainPlugin)
    p.set_parameter("turbulence", turb)
    feats = dict(LOUD, frequency_bands={"bass": 0, "mid": 0, "treble": 1.0})
    xs = []
    for part in p.particles[:300]:
        part.acceleration.x = 0
    p.update(feats, 1 / 60)
    xs = [abs(part.acceleration.x - part.gravity.x) for part in p.particles[:300]]
    return max(xs)


def test_fountain_turbulence():
    assert _spread(0.0) < 1e-12
    assert _spread(0.4) > 2 * _spread(0.1)


def test_noise_sphere_beat_sensitivity():
    lo, hi = make(NoiseSpherePlugin), make(NoiseSpherePlugin)
    lo.set_parameter("beat_sensitivity", 0.5)
    hi.set_parameter("beat_sensitivity", 2.0)
    feats = dict(LOUD, amplitude=0.2)
    lo.update(feats, 1 / 60)
    hi.update(feats, 1 / 60)
    assert hi.hairs[0].beat_response > 3 * lo.hairs[0].beat_response > 0


def _coherence_after(seconds, coherence_time):
    p = make(QuantumJazzPlugin)
    p.set_parameter("quantum_coherence_time", coherence_time)
    q = QuantumParticle(400, 300, 1)
    q.coherence_time = coherence_time
    q.observe_particle(0.5)
    q.collapse_timer = seconds - 1 / 60
    q.update(1 / 60, {"amplitude": 0, "beat_detected": False}, [q])
    return q.coherence


def test_quantum_coherence_time():
    assert abs(_coherence_after(2.5, 5.0) - 0.5) < 1e-6
    assert abs(_coherence_after(2.5, 10.0) - 0.75) < 1e-6
    p = make(QuantumJazzPlugin)
    p.particles = [QuantumParticle(400, 300, 1)]
    p.set_parameter("quantum_coherence_time", 8.0)
    p.update({"amplitude": 0, "beat_detected": False}, 1 / 60)
    assert all(q.coherence_time == 8.0 for q in p.particles)


def test_quantum_beat_observation_strength():
    seen = []
    q = QuantumParticle(400, 300, 1)
    q.observe_particle = lambda intensity: seen.append(intensity)
    q.observation_strength = 4.0
    q.update(1 / 60, {"amplitude": 0.3, "beat_detected": True}, [q])
    assert abs(seen[0] - 0.6) < 1e-12
