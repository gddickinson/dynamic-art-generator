"""Regressions: Rehoboam's build_network() must rebuild the rings instead of stacking new ones on the old ones
(reset() or a num_rings change doubled the network), and the Ecosystem predator must sprint only when close to its
prey (it measured the distance after normalising the direction, so it always sprinted)."""
from plugin_test_utils import make

from plugins.ecosystem import Predator, Vector2D
from plugins.rehoboam import RehoboamPlugin


def test_rehoboam_reset_keeps_ring_count():
    p = make(RehoboamPlugin)
    n = len(p.rings)
    assert n == int(p.num_rings)
    p.reset()
    assert len(p.rings) == n
    p.set_parameter("num_rings", 4)
    assert len(p.rings) == 4


def test_predator_sprints_only_when_close():
    def desired_speed(target):
        pred = Predator(100, 100)          # at rest, so steer = desired velocity once the force limit is lifted
        pred.beat_boost = 0.0
        pred.maxforce = 1e9
        return pred.seek(target).x, pred.maxspeed
    v, maxspeed = desired_speed(Vector2D(400, 100))    # 300 px away
    assert abs(v - maxspeed) < 1e-9
    v, maxspeed = desired_speed(Vector2D(110, 100))    # 10 px away: sprint
    assert abs(v - 2 * maxspeed) < 1e-9
