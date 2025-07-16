#!/usr/bin/env python3
"""
Dynamic Art Generator - Utilities Package
Common utilities and helper functions

Author: Claude Assistant
Version: 1.0
"""

# Make utilities easily importable
try:
    from .audio_utils import (
        AudioAnalyzer, 
        DrumMachine, 
        AudioSmoother, 
        normalize_audio_features,
        create_audio_visualizer_data
    )
except ImportError:
    print("Audio utilities not available - some features may be limited")
    AudioAnalyzer = None
    DrumMachine = None
    AudioSmoother = None

try:
    from .math_utils import (
        Vector2D,
        ColorUtils,
        GeometryUtils,
        PhysicsUtils,
        NoiseUtils,
        InterpolationUtils,
        MathUtils,
        Constants
    )
except ImportError:
    print("Math utilities not available - some features may be limited")
    Vector2D = None
    ColorUtils = None
    GeometryUtils = None

# Version information
__version__ = "1.0.0"
__author__ = "Claude Assistant"

# Package information
UTILS_INFO = {
    "audio_processing": AudioAnalyzer is not None,
    "math_utilities": Vector2D is not None,
    "version": __version__
}

def get_utils_info():
    """Get information about available utilities"""
    return UTILS_INFO

# Common color constants for easy access
class Colors:
    """Common color constants"""
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)

# Common utility functions
def clamp(value, min_val, max_val):
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def lerp(a, b, t):
    """Linear interpolation between a and b"""
    return a + (b - a) * clamp(t, 0, 1)

def map_range(value, in_min, in_max, out_min, out_max):
    """Map value from one range to another"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Export commonly used items
__all__ = [
    'AudioAnalyzer', 'DrumMachine', 'AudioSmoother',
    'Vector2D', 'ColorUtils', 'GeometryUtils', 'PhysicsUtils',
    'NoiseUtils', 'InterpolationUtils', 'MathUtils', 'Constants',
    'Colors', 'clamp', 'lerp', 'map_range', 'get_utils_info'
]
