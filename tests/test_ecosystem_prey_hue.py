"""Regression: Musical Ecosystem prey colour must respond to the audio.

Boid.update_audio_response added a frequency/amplitude hue shift and then overwrote it on the next line with a hue
from age alone, so prey never changed colour with the music (its docstring: "Update color and visual response to
audio"). The prey hue is now age hue + audio shift, computed afresh each frame like the predators' hue.
"""
from plugin_test_utils import SILENT  # noqa: F401  (sets up headless pygame)

from plugins.ecosystem import Boid


def hue(amplitude, frequency, age=5.0):
    b = Boid(100, 100)
    b.age, b.max_age = age, 20.0
    b.update_audio_response({"amplitude": amplitude, "dominant_frequency": frequency})
    return b.color_hue


def test_prey_hue_follows_audio():
    assert abs(hue(0.0, 0.0) - 75.0) < 1e-9                      # age hue: 60 + (5/20) * 60
    assert abs(hue(1.0, 1000.0) - (75.0 + 2.0 + 10.0)) < 1e-9    # + frequency * 0.002 + amplitude * 10


def test_prey_hue_does_not_drift():
    b = Boid(100, 100)
    b.age, b.max_age = 5.0, 20.0
    for _ in range(100):
        b.update_audio_response({"amplitude": 0.5, "dominant_frequency": 440.0})
    assert abs(b.color_hue - (75.0 + 0.88 + 5.0)) < 1e-9
