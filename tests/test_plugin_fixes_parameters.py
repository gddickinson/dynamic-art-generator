"""Regressions: plugin parameters shown as desktop sliders/checkboxes that had no effect now act on the art.

Each was stored by set_parameter() but never read. They are wired so that their default value reproduces the previous
behaviour exactly; these tests check that changing them changes what the plugin does.
"""
import random

import pygame
from plugin_test_utils import LOUD, SILENT, make

from plugins import ecosystem, neural_flow
from plugins.biomech_garden import BioMechGardenPlugin, GearFlower
from plugins.cosmic_web import CosmicOrb, CosmicWebPlugin
from plugins.musical_flock import MusicalFlockPlugin
from plugins.neural_flow import NeuralFlowPlugin
from plugins.particle_fountain import ParticleFountainPlugin


def test_flock_radii_and_speed_reach_the_boids():
    p = make(MusicalFlockPlugin)
    p.set_parameter("separation_radius", 50.0)
    p.set_parameter("neighbor_radius", 80.0)
    p.set_parameter("max_speed", 4.0)
    p.update(SILENT, 1 / 60)
    b = p.boids[0]
    assert (b.desired_separation, b.neighbor_dist, b.base_maxspeed) == (50.0, 80.0, 4.0)
    other = make(MusicalFlockPlugin).boids[0]
    b.location.x, b.location.y = 100, 100
    other.location.x, other.location.y = 140, 100                # 40 px apart: inside 50, outside the old 25
    assert b.separate([b, other]).mag() > 0


def test_fountain_gravity_survives_reset_and_wind_pushes_sideways():
    p = make(ParticleFountainPlugin)
    p.set_parameter("gravity_strength", 2.0)
    p.set_parameter("wind_force", 1.0)
    assert all(abs(q.gravity.x - 0.15) < 1e-12 for q in p.particles)
    p.reset()
    assert all(abs(q.gravity.y - 0.3) < 1e-12 and abs(q.gravity.x - 0.15) < 1e-12 for q in p.particles)


def _cosmic_run(strength):
    random.seed(3)
    p = make(CosmicWebPlugin)
    a, b = CosmicOrb(300, 300), CosmicOrb(500, 300)
    for o in (a, b):
        o.vx = o.vy = 0.0
    p.orbs = [a, b]
    p.set_parameter("gravity_strength", strength)
    for _ in range(30):
        p.update(SILENT, 1 / 60)
    return a.x


def test_cosmic_gravity_strength_changes_attraction():
    assert _cosmic_run(0.0) != _cosmic_run(5.0)


def _petals(enable):
    p = make(BioMechGardenPlugin)
    f = GearFlower(400, 300)
    f.bloom_state, f.servo_angle = 1.0, 30.0
    p.flowers = [f]
    p.set_parameter("enable_servo_animation", enable)
    s = pygame.Surface((800, 600))
    p.render_flowers(s)
    f.servo_angle = 0.0
    s0 = pygame.Surface((800, 600))
    p.render_flowers(s0)
    return pygame.image.tobytes(s, "RGB") == pygame.image.tobytes(s0, "RGB")


def test_biomech_servo_animation_switch():
    assert _petals(False)          # switched off: petals do not swing with the servo
    assert not _petals(True)


def test_neural_clustering_switch_and_breathing(monkeypatch):
    p = make(NeuralFlowPlugin)
    p.set_parameter("enable_clustering", False)
    monkeypatch.setattr(neural_flow.FlowParticle, "apply_clustering_forces",
                        lambda *a: (_ for _ in ()).throw(AssertionError("clustering ran")))
    p.update(SILENT, 1 / 60)
    monkeypatch.undo()
    p.set_parameter("organic_breathing", 0.0)
    p.update(SILENT, 1 / 60)
    q = p.particles[0]
    assert q.breathing_scale == 0.0


def test_ecosystem_audio_sensitivity_and_aggression(monkeypatch):
    p = make(ecosystem.MusicalEcosystemPlugin)
    p.set_parameter("audio_sensitivity", 0.0)
    p.set_parameter("predator_aggression_multiplier", 3.0)
    seen = []
    real = ecosystem.Boid.update

    def spy(self, dt, boids, predators, features, bounds):
        seen.append(features["amplitude"])
        return real(self, dt, boids, predators, features, bounds)
    monkeypatch.setattr(ecosystem.Boid, "update", spy)
    p.update(LOUD, 1 / 60)
    assert seen and all(a == 0.0 for a in seen)
    assert all(pr.aggression == 3.0 for pr in p.predators)

