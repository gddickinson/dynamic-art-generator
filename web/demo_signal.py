"""Built-in demo signal for the web app, so the art has something to react to with no file or microphone.

Ported line by line to static/demo_signal.js; tests/fixtures/audio_reference.json (scripts/make_fixtures.py) analyses
this signal with the repo's AudioAnalyzer so the JS analysis is checked on identical input.

  drums  the kick, snare and hi-hat sounds of utils.audio_utils.DrumMachine (same formulas, durations and noise levels;
         the Gaussian noise comes from mulberry32 so the browser can regenerate it exactly) at the DrumMachine's
         default 120 BPM: kick on beats 1 and 3, snare on 2 and 4, hi-hat on every eighth note
  tone   a sine whose pitch glides between 240 and 640 Hz (440 +/- 200 Hz, the range of the simulated
         dominant_frequency in launcher.py / macos_demo.py) once per loop
"""
import math

import numpy as np

RATE = 44100
BPM = 120.0                # DrumMachine default
LOOP_SECONDS = 16.0        # 8 bars of 4/4 at 120 BPM
GAIN = {"kick": 0.6, "snare": 0.3, "hihat": 0.12, "tone": 0.2}
M32 = 0xFFFFFFFF


class Mulberry32:
    """mulberry32, bit-for-bit the same stream as rng(seed) in static/core.js and pyrand.js."""

    def __init__(self, seed):
        self.a = seed & M32

    def __call__(self):
        self.a = (self.a + 0x6D2B79F5) & M32
        a = self.a
        t = ((a ^ (a >> 15)) * (1 | a)) & M32
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & M32)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296.0

    def gauss(self):
        """Standard normal by Box-Muller (two draws), as gauss() in static/demo_signal.js."""
        u = 0.0
        while u == 0.0:
            u = self()
        return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * self())


def _t(duration):
    return np.linspace(0, duration, int(RATE * duration))


def drum_sounds(seed=1):
    """DrumMachine._generate_kick/_snare/_hihat with mulberry32 Gaussian noise in place of np.random.normal."""
    rnd = Mulberry32(seed)
    t = _t(0.2)
    amp = np.exp(-t * 8)
    kick = amp * np.sin(2 * np.pi * (60 * np.exp(-t * 30)) * t)
    kick = kick + np.array([0.1 * rnd.gauss() for _ in t]) * amp * 0.3
    t = _t(0.15)
    snare = np.exp(-t * 15) * (0.3 * np.sin(2 * np.pi * 200 * t) + np.array([rnd.gauss() for _ in t]) * 0.7)
    t = _t(0.1)
    hihat = np.array([rnd.gauss() for _ in t]) * np.exp(-t * 40) * 0.5
    return {"kick": kick, "snare": snare, "hihat": hihat}


def demo_signal(n=None, seed=1):
    """The demo loop as float64 samples (n defaults to one full loop)."""
    n = int(LOOP_SECONDS * RATE) if n is None else n
    k = np.arange(n)
    t = k / RATE
    w = 2 * math.pi / LOOP_SECONDS
    # phase of f(t) = 440 + 200 sin(w t), integrated in closed form
    out = GAIN["tone"] * np.sin(2 * math.pi * (440 * t + 200 / w * (1 - np.cos(w * t))))
    sounds = drum_sounds(seed)
    eighth = int(round(RATE * 30.0 / BPM))
    for i, start in enumerate(range(0, n, eighth)):
        beat_in_bar, on_beat = (i // 2) % 4, i % 2 == 0
        hits = ["hihat"]
        if on_beat:
            hits.append("kick" if beat_in_bar in (0, 2) else "snare")
        for name in hits:
            s = sounds[name][: n - start]
            out[start:start + len(s)] += GAIN[name] * s
    return out
