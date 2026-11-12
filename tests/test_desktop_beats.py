"""Regression: desktop beat detection must be adaptive, not "RMS > 0.1".

With the fixed rule every chunk of loud, steady music counted as a beat, so plugins that react to beats (bursts,
impulses, collapses) fired 43 times a second. Beats now come from AudioAnalyzer.detect_beat: chunk energy against the
running average of the last 20 chunks plus 1.5 standard deviations, at most one beat per 0.1 s.
"""
import sys
import types
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import audio_utils  # noqa: E402
from utils.audio_utils import AudioAnalyzer  # noqa: E402
from utils.desktop_features import desktop_audio_features  # noqa: E402

RATE, N = 44100, 1024


def run(chunks, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(audio_utils, "time", types.SimpleNamespace(time=lambda: clock[0]))
    an, beats = AudioAnalyzer(RATE, N), []
    for i, c in enumerate(chunks):
        clock[0] = 1000.0 + i * N / RATE
        beats.append(bool(desktop_audio_features(c, RATE, an)["beat_detected"]))
    return beats


def test_loud_steady_tone_is_not_a_constant_beat(monkeypatch):
    tone = 0.5 * np.sin(2 * np.pi * 440 * np.arange(N) / RATE)     # RMS 0.35 > 0.1
    assert sum(run([tone] * 60, monkeypatch)) == 0


def test_hits_over_quiet_background_are_beats(monkeypatch):
    hum = 0.02 * np.sin(2 * np.pi * 10 * np.arange(N) / N)          # quiet, identical in every chunk
    quiet = [hum.copy() for _ in range(80)]
    hits = list(range(30, 80, 11))                                    # a hit every ~0.26 s
    for i in hits:
        quiet[i] = quiet[i] + 0.6 * np.sin(2 * np.pi * 60 * np.arange(N) / RATE)
    assert [i for i, b in enumerate(run(quiet, monkeypatch)) if b] == hits
