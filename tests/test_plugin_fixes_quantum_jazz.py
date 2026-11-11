"""Regressions for plugins/quantum_jazz.py: particle_creation_rate 0 must not crash (ZeroDivisionError on 1 / rate;
0 is the bottom of the desktop slider), and trail segments heading left or up must be drawn."""
import time

from plugin_test_utils import LOUD, black, lit_near, make

from plugins.quantum_jazz import QuantumJazzPlugin, QuantumParticle


def test_zero_creation_rate_creates_nothing_and_does_not_crash():
    p = make(QuantumJazzPlugin)
    p.set_parameter("particle_creation_rate", 0.0)
    n = len(p.particles)
    for _ in range(120):
        p.update(LOUD, 1 / 60)
    assert len(p.particles) <= n


def test_trail_segment_up_left_is_drawn():
    p = make(QuantumJazzPlugin)
    q = QuantumParticle(400, 300)
    now = time.time()
    q.trail = [(400, 300, now), (340, 240, now)]
    p.particles = [q]
    s = black()
    p.render_particle_trails(s)
    assert lit_near(s, 370, 270)
