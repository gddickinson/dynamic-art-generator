"""Regression: the Particles plugin must not crash when particle_life is 0.

The desktop parameter sliders run from 0 to twice the default, so particle_life = 0 is reachable; Particle.update
divided by max_life and raised ZeroDivisionError on the next frame.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from plugins.particles import Particle, ParticlePlugin  # noqa: E402

FEATURES = {"amplitude": 0.6, "beat_detected": True, "dominant_frequency": 440.0,
            "frequency_bands": {"bass": 0.4, "mid": 0.4, "treble": 0.2}}


def test_zero_lifetime_particle_dies_without_error():
    p = Particle(10, 10, 1, 1, 0.0, (255, 0, 0))
    p.update(1 / 60, (0, 0), (800, 600))
    assert not p.is_alive()


def test_plugin_runs_with_particle_life_zero():
    pygame.init()
    surface = pygame.Surface((800, 600))
    plugin = ParticlePlugin((800, 600))
    plugin.set_parameter("particle_life", 0.0)
    for _ in range(5):
        plugin.update(FEATURES, 1 / 60)
        plugin.render(surface)
