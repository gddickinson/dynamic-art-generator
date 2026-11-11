"""Shared helpers for the plugin regression tests: headless pygame, quiet plugin construction, feature dicts."""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

pygame.init()
SIZE = (800, 600)

LOUD = {"amplitude": 0.6, "beat_detected": True, "dominant_frequency": 440.0,
        "frequency_bands": {"bass": 0.4, "mid": 0.4, "treble": 0.2}}
SILENT = {"amplitude": 0.0, "beat_detected": False, "dominant_frequency": 0.0,
          "frequency_bands": {"bass": 0.0, "mid": 0.0, "treble": 0.0}}


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def make(cls):
    return quiet(cls, SIZE)


def black():
    s = pygame.Surface(SIZE)
    s.fill((0, 0, 0))
    return s


def lit(surface, x, y):
    return sum(surface.get_at((int(x), int(y)))[:3]) > 0


def lit_near(surface, x, y, r=2):
    """Any lit pixel within r pixels of (x, y) (rotation and rounding move thin lines by a pixel)."""
    return any(lit(surface, x + dx, y + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1))
