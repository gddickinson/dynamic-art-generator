"""Regressions for plugins/biomech_garden.py: vines survive, data-network lines land between the components, gears
with high energy are still drawn."""
import random

from plugin_test_utils import SILENT, black, lit, lit_near, make

from plugins.biomech_garden import BioMechGardenPlugin, GearFlower


def test_new_vines_are_not_dropped():
    random.seed(1)
    p = make(BioMechGardenPlugin)
    n = len(p.vines)
    assert n > 0
    p.update(SILENT, 1 / 60)
    assert len(p.vines) == n


def test_network_line_drawn_between_components():
    p = make(BioMechGardenPlugin)
    p.vines = []
    p.flowers = [GearFlower(400, 300), GearFlower(340, 300)]   # second one to the LEFT of the first
    p.data_network_activity = 1.0
    s = black()
    p.render_data_network(s)
    assert lit_near(s, 370, 300)        # midpoint of the connection
    assert not lit_near(s, 430, 300)    # mirrored to the wrong side before the fix


def test_gear_drawn_when_energy_is_high():
    p = make(BioMechGardenPlugin)
    s = black()
    p.render_gear(s, {"x": 200, "y": 200, "size": 8, "rotation": 0, "type": "gear"}, 2.0)
    assert lit(s, 200, 200)
