"""Regressions: lines drawn on a temporary alpha surface must land between their two end points.

Cosmic Web connections, Noise Sphere hairs and Neural Flow connections were drawn relative to the START point but the
temporary surface was blitted at the top-left corner of the pair, so every line heading left or up was drawn outside
its surface (clipped away) or displaced.
"""
from plugin_test_utils import black, lit_near, make

from plugins.cosmic_web import CosmicOrb, CosmicWebPlugin
from plugins.neural_flow import FlowParticle, NeuralFlowPlugin
from plugins.noise_sphere import NoiseSpherePlugin

START, END, MID = (400, 300), (340, 240), (370, 270)   # END is up and to the left of START


def test_cosmic_web_connection_up_left():
    p = make(CosmicWebPlugin)
    a, b = CosmicOrb(*START), CosmicOrb(*END)
    a.connections, b.connections = {id(b): 1.0}, {}
    p.orbs = [a, b]
    s = black()
    p.render_connections(s)
    assert lit_near(s, *MID)


def test_noise_sphere_hair_up_left():
    p = make(NoiseSpherePlugin)
    assert p.hair_alpha < 255          # the temporary-surface path
    s = black()
    p.render_single_hair(s, p.hairs[0], START, END, 0.0)
    assert lit_near(s, *MID)


def test_neural_flow_connection_up_left():
    p = make(NeuralFlowPlugin)
    a, b = FlowParticle(*START), FlowParticle(*END)
    a.energy = b.energy = 1.0
    s = black()
    p.draw_organic_connection(s, a, b, 1.0)
    assert lit_near(s, *MID)


def test_lines_down_right_still_drawn():
    p = make(NoiseSpherePlugin)
    s = black()
    p.render_single_hair(s, p.hairs[0], END, START, 0.0)
    assert lit_near(s, *MID)
