"""Regression for plugins/space_junk.py: the scene rotation is specified in degrees (20 degrees per second at
rotation_speed 1) but the value was used directly as radians by Vector3D.rotate_*, so the scene spun about 57 times too
fast (over three turns per second)."""
import math

from plugin_test_utils import SILENT, make

from plugins.space_junk import SpaceJunkPlugin


def test_scene_rotates_20_degrees_per_second():
    p = make(SpaceJunkPlugin)
    for _ in range(60):
        p.update(SILENT, 1 / 60)
    assert abs(p.global_rotation.y - math.radians(20)) < 1e-6
    assert abs(p.global_rotation.x - math.radians(14)) < 1e-6
