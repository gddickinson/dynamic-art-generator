"""Reference run of the repo's audio feature extraction on the built-in demo signal (for the JS port and the web
Verify page).

The demo signal (web/demo_signal.py) is cut into consecutive 1024-sample chunks at 44.1 kHz (config.json audio
chunk_size / sample_rate) and each chunk goes through utils.desktop_features.desktop_audio_features with a real
utils.audio_utils.AudioAnalyzer, exactly as main.AudioProcessor does. AudioAnalyzer reads time.time() for beat spacing
and tempo; here the clock is the stream time (chunk index x 1024 / 44100 s from 1000 s), as the browser does.
"""
import math
import types
from contextlib import contextmanager

import numpy as np

from utils import audio_utils
from utils.audio_utils import AudioAnalyzer
from utils.desktop_features import desktop_audio_features

from .demo_signal import LOOP_SECONDS, RATE, demo_signal

CHUNK = 1024
N_CHUNKS = 240          # about 5.6 s: covers several bars of the demo
T0 = 1000.0
SCALARS = ["amplitude", "rms", "dominant_frequency", "spectral_centroid", "estimated_tempo", "harmonicity",
           "spectral_rolloff", "zero_crossing_rate", "frequency"]
FLAGS = ["beat_detected", "onset_detected"]


@contextmanager
def stream_clock(clock):
    real = audio_utils.time
    audio_utils.time = types.SimpleNamespace(time=lambda: clock[0])
    try:
        yield
    finally:
        audio_utils.time = real


def analyse(signal, n_chunks, analyzer_beats=True):
    """Rows of features for consecutive chunks (desktop definitions + AudioAnalyzer keys)."""
    clock = [T0]
    rows = []
    with stream_clock(clock):
        an = AudioAnalyzer(RATE, CHUNK)
        an_raw = AudioAnalyzer(RATE, CHUNK)   # analyzer's own amplitude/beat (before the desktop overrides)
        for i in range(n_chunks):
            clock[0] = T0 + i * CHUNK / RATE
            chunk = signal[i * CHUNK:(i + 1) * CHUNK]
            f = desktop_audio_features(chunk, RATE, an)
            raw = an_raw.analyze_audio(chunk)
            row = {k: float(f[k]) for k in SCALARS}
            row.update({k: bool(f[k]) for k in FLAGS})
            row["bands"] = [float(f["frequency_bands"][b]) for b in ("bass", "mid", "treble")]
            row["analyzer_amplitude"] = float(raw["amplitude"])
            row["analyzer_beat"] = bool(raw["beat_detected"])
            rows.append(row)
    return rows


def reference():
    sig = demo_signal(N_CHUNKS * CHUNK)
    full = demo_signal()
    probe = list(range(0, len(full), 9973))
    return {
        "rate": RATE, "chunk": CHUNK, "t0": T0, "loop_seconds": LOOP_SECONDS,
        "rows": analyse(sig, N_CHUNKS),
        "demo_head": [float(v) for v in sig[:256]],
        "demo_probe": {"index": probe, "value": [float(full[i]) for i in probe]},
        "demo_abs_sum": float(np.abs(full).sum()),
        "demo_peak": float(np.abs(full).max()),
    }


def summary(rows):
    """Small numbers for the Verify page header."""
    beats = sum(r["beat_detected"] for r in rows)
    return {"chunks": len(rows), "desktop_beats": beats, "analyzer_beats": sum(r["analyzer_beat"] for r in rows),
            "seconds": round(len(rows) * CHUNK / RATE, 2), "mean_rms": float(np.mean([r["amplitude"] for r in rows])),
            "dominant_hz_range": [min(r["dominant_frequency"] for r in rows), max(r["dominant_frequency"] for r in rows)],
            "nan": any(math.isnan(v) for r in rows for v in r["bands"])}
