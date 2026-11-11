"""Regression: the desktop AudioProcessor must give the plugins the features they read.

Every plugin reads audio_features['dominant_frequency'] and ['frequency_bands'], but main.AudioProcessor only produced
amplitude, frequency, beat_detected and raw_data, so with a real microphone the frequency- and band-driven behaviour
never responded. The features now include the AudioAnalyzer keys (amplitude/beat keep their desktop definitions).
"""
import os
import sys
import types
from pathlib import Path

import numpy as np

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main  # noqa: E402

RATE, N = 44100, 1024


def tone(freq, level=0.5):
    return (level * np.sin(2 * np.pi * freq * np.arange(N) / RATE)).astype(np.float32)


def test_audio_processor_features_include_plugin_keys(monkeypatch):
    if not hasattr(main, "pyaudio"):
        monkeypatch.setattr(main, "pyaudio", types.SimpleNamespace(paContinue=0), raising=False)
    proc = main.AudioProcessor.__new__(main.AudioProcessor)   # no sound card needed
    proc.sample_rate, proc.chunk_size = RATE, N
    proc.audio = proc.stream = None
    proc.audio_data = np.zeros(N)
    proc.amplitude = proc.frequency = 0.0
    proc.beat_detected = False
    proc.analyzer = main.AudioAnalyzer(RATE, N) if main.UTILS_AVAILABLE else None
    proc.audio_callback(tone(2000).tobytes(), N, None, None)
    f = proc.get_audio_features()
    assert abs(f["dominant_frequency"] - 2000) < RATE / N
    assert set(f["frequency_bands"]) == {"bass", "mid", "treble"}
    assert f["frequency_bands"]["mid"] > 0.9
    # desktop definitions unchanged
    assert abs(f["amplitude"] - 0.5 / np.sqrt(2)) < 1e-3
    assert f["beat_detected"] is True or f["beat_detected"] == np.True_
    assert abs(f["frequency"] - 2000) < RATE / N


def test_desktop_audio_features_pure_function():
    from utils.audio_utils import AudioAnalyzer
    from utils.desktop_features import desktop_audio_features
    f = desktop_audio_features(tone(100, 0.05), RATE, AudioAnalyzer(RATE, N))
    assert f["frequency_bands"]["bass"] > 0.9
    assert not f["beat_detected"]            # RMS 0.035 < 0.1
    assert "raw_data" in f and len(f["raw_data"]) == N
