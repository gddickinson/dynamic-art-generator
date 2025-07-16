#!/usr/bin/env python3
"""
Audio Utilities for Dynamic Art Generator - Fixed Version
Provides advanced audio analysis and processing functions

Author: Claude Assistant
Version: 1.1 - Array Shape Fix
"""

import numpy as np
import time
from typing import List, Tuple, Dict, Optional
from collections import deque
import math

class AudioAnalyzer:
    """Advanced audio analysis with beat detection, frequency analysis, and more"""

    def __init__(self, sample_rate=44100, window_size=1024):
        self.sample_rate = sample_rate
        self.window_size = window_size

        # Beat detection
        self.energy_history = deque(maxlen=43)  # ~1 second at 43 FPS
        self.beat_threshold = 1.5
        self.beat_sensitivity = 1.0
        self.last_beat_time = 0
        self.min_beat_interval = 0.1  # Minimum seconds between beats

        # Frequency analysis
        self.freq_bins = np.fft.rfftfreq(window_size, 1/sample_rate)
        self.freq_history = deque(maxlen=10)

        # Onset detection
        self.onset_threshold = 0.3
        self.spectral_flux_history = deque(maxlen=10)

        # Tempo estimation
        self.tempo_history = deque(maxlen=20)
        self.estimated_tempo = 120  # BPM

    def analyze_audio(self, audio_data: np.ndarray) -> Dict:
        """Comprehensive audio analysis"""
        if len(audio_data) == 0:
            return self._empty_features()

        # Basic features
        amplitude = self.calculate_amplitude(audio_data)
        rms = self.calculate_rms(audio_data)

        # Frequency analysis
        frequencies, magnitudes = self.analyze_frequency(audio_data)
        dominant_freq = self.get_dominant_frequency(frequencies, magnitudes)
        spectral_centroid = self.calculate_spectral_centroid(frequencies, magnitudes)

        # Beat detection
        beat_detected = self.detect_beat(audio_data)

        # Onset detection
        onset_detected = self.detect_onset(audio_data)

        # Tempo estimation
        self.update_tempo_estimation(beat_detected)

        # Harmonic content
        harmonicity = self.calculate_harmonicity(frequencies, magnitudes)

        # Spectral features
        spectral_rolloff = self.calculate_spectral_rolloff(frequencies, magnitudes)
        zero_crossing_rate = self.calculate_zero_crossing_rate(audio_data)

        return {
            'amplitude': amplitude,
            'rms': rms,
            'dominant_frequency': dominant_freq,
            'spectral_centroid': spectral_centroid,
            'beat_detected': beat_detected,
            'onset_detected': onset_detected,
            'estimated_tempo': self.estimated_tempo,
            'harmonicity': harmonicity,
            'spectral_rolloff': spectral_rolloff,
            'zero_crossing_rate': zero_crossing_rate,
            'frequency_bands': self.analyze_frequency_bands(frequencies, magnitudes),
            'raw_audio': audio_data.copy()
        }

    def calculate_amplitude(self, audio_data: np.ndarray) -> float:
        """Calculate peak amplitude"""
        return float(np.max(np.abs(audio_data)))

    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calculate RMS (Root Mean Square) energy"""
        return float(np.sqrt(np.mean(audio_data ** 2)))

    def analyze_frequency(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Perform FFT analysis"""
        if len(audio_data) == 0:
            return np.array([]), np.array([])

        # Apply window to reduce spectral leakage
        windowed = audio_data * np.hanning(len(audio_data))
        fft = np.fft.rfft(windowed)
        magnitudes = np.abs(fft)

        # Get corresponding frequencies
        frequencies = np.fft.rfftfreq(len(audio_data), 1/self.sample_rate)

        # Ensure both arrays have the same length
        min_length = min(len(frequencies), len(magnitudes))
        frequencies = frequencies[:min_length]
        magnitudes = magnitudes[:min_length]

        return frequencies, magnitudes

    def get_dominant_frequency(self, frequencies: np.ndarray, magnitudes: np.ndarray) -> float:
        """Get the dominant frequency"""
        if len(magnitudes) == 0:
            return 0.0
        peak_idx = np.argmax(magnitudes)
        if peak_idx < len(frequencies):
            return float(frequencies[peak_idx])
        return 0.0

    def calculate_spectral_centroid(self, frequencies: np.ndarray, magnitudes: np.ndarray) -> float:
        """Calculate spectral centroid (brightness)"""
        if np.sum(magnitudes) == 0 or len(frequencies) == 0 or len(magnitudes) == 0:
            return 0.0

        # Ensure frequencies and magnitudes have the same length
        min_length = min(len(frequencies), len(magnitudes))
        frequencies = frequencies[:min_length]
        magnitudes = magnitudes[:min_length]

        return float(np.sum(frequencies * magnitudes) / np.sum(magnitudes))

    def detect_beat(self, audio_data: np.ndarray) -> bool:
        """Simple beat detection using energy-based method"""
        current_energy = np.sum(audio_data ** 2)
        self.energy_history.append(current_energy)

        if len(self.energy_history) < 20:
            return False

        # Calculate local energy average
        local_avg = np.mean(list(self.energy_history)[-20:])
        variance = np.var(list(self.energy_history)[-20:])

        # Adaptive threshold
        threshold = local_avg + self.beat_threshold * np.sqrt(variance)

        # Check if current energy exceeds threshold and enough time has passed
        current_time = time.time()
        if (current_energy > threshold and
            current_time - self.last_beat_time > self.min_beat_interval):
            self.last_beat_time = current_time
            return True

        return False

    def detect_onset(self, audio_data: np.ndarray) -> bool:
        """Onset detection using spectral flux"""
        frequencies, magnitudes = self.analyze_frequency(audio_data)

        if len(self.spectral_flux_history) == 0:
            self.spectral_flux_history.append(magnitudes)
            return False

        # Calculate spectral flux
        prev_magnitudes = self.spectral_flux_history[-1]

        # Ensure same length for comparison
        min_length = min(len(magnitudes), len(prev_magnitudes))
        current_mags = magnitudes[:min_length]
        prev_mags = prev_magnitudes[:min_length]

        flux = np.sum(np.maximum(0, current_mags - prev_mags))

        self.spectral_flux_history.append(magnitudes)

        # Simple threshold-based onset detection
        return flux > self.onset_threshold

    def update_tempo_estimation(self, beat_detected: bool):
        """Update estimated tempo based on beat intervals"""
        if beat_detected:
            current_time = time.time()
            if hasattr(self, 'last_tempo_beat_time'):
                interval = current_time - self.last_tempo_beat_time
                if 0.3 < interval < 2.0:  # Reasonable tempo range
                    bpm = 60.0 / interval
                    self.tempo_history.append(bpm)
                    # Smooth tempo estimation
                    self.estimated_tempo = np.median(list(self.tempo_history))
            self.last_tempo_beat_time = current_time

    def calculate_harmonicity(self, frequencies: np.ndarray, magnitudes: np.ndarray) -> float:
        """Calculate how harmonic the sound is"""
        if len(magnitudes) < 10:
            return 0.0

        # Find peaks
        peaks = []
        for i in range(1, len(magnitudes) - 1):
            if magnitudes[i] > magnitudes[i-1] and magnitudes[i] > magnitudes[i+1]:
                if i < len(frequencies):
                    peaks.append((frequencies[i], magnitudes[i]))

        if len(peaks) < 2:
            return 0.0

        # Sort peaks by magnitude
        peaks.sort(key=lambda x: x[1], reverse=True)

        # Check if peaks are harmonically related
        fundamental = peaks[0][0]
        if fundamental < 20:  # Too low to be meaningful
            return 0.0

        harmonic_strength = 0.0
        for freq, mag in peaks[1:6]:  # Check first 5 harmonics
            harmonic_ratio = freq / fundamental
            # Check if it's close to an integer ratio
            closest_harmonic = round(harmonic_ratio)
            if abs(harmonic_ratio - closest_harmonic) < 0.1:
                harmonic_strength += mag

        return min(1.0, harmonic_strength / sum(mag for _, mag in peaks[:6]))

    def calculate_spectral_rolloff(self, frequencies: np.ndarray, magnitudes: np.ndarray,
                                 threshold: float = 0.85) -> float:
        """Calculate spectral rolloff frequency"""
        if len(magnitudes) == 0:
            return 0.0

        total_energy = np.sum(magnitudes)
        if total_energy == 0:
            return 0.0

        cumulative_energy = np.cumsum(magnitudes)
        rolloff_threshold = threshold * total_energy

        rolloff_idx = np.where(cumulative_energy >= rolloff_threshold)[0]
        if len(rolloff_idx) == 0:
            return frequencies[-1] if len(frequencies) > 0 else 0.0

        idx = rolloff_idx[0]
        if idx < len(frequencies):
            return float(frequencies[idx])
        return 0.0

    def calculate_zero_crossing_rate(self, audio_data: np.ndarray) -> float:
        """Calculate zero crossing rate (measure of noisiness)"""
        if len(audio_data) < 2:
            return 0.0

        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data))))
        return float(zero_crossings / (2 * len(audio_data)))

    def analyze_frequency_bands(self, frequencies: np.ndarray, magnitudes: np.ndarray) -> Dict:
        """Analyze energy in different frequency bands"""
        if len(frequencies) == 0 or len(magnitudes) == 0:
            return {'bass': 0, 'mid': 0, 'treble': 0}

        # Ensure same length
        min_length = min(len(frequencies), len(magnitudes))
        frequencies = frequencies[:min_length]
        magnitudes = magnitudes[:min_length]

        # Define frequency bands
        bass_mask = frequencies <= 250
        mid_mask = (frequencies > 250) & (frequencies <= 4000)
        treble_mask = frequencies > 4000

        bass_energy = np.sum(magnitudes[bass_mask]) if np.any(bass_mask) else 0
        mid_energy = np.sum(magnitudes[mid_mask]) if np.any(mid_mask) else 0
        treble_energy = np.sum(magnitudes[treble_mask]) if np.any(treble_mask) else 0

        # Normalize
        total_energy = bass_energy + mid_energy + treble_energy
        if total_energy > 0:
            bass_energy /= total_energy
            mid_energy /= total_energy
            treble_energy /= total_energy

        return {
            'bass': float(bass_energy),
            'mid': float(mid_energy),
            'treble': float(treble_energy)
        }

    def _empty_features(self) -> Dict:
        """Return empty feature set"""
        return {
            'amplitude': 0.0,
            'rms': 0.0,
            'dominant_frequency': 0.0,
            'spectral_centroid': 0.0,
            'beat_detected': False,
            'onset_detected': False,
            'estimated_tempo': 120.0,
            'harmonicity': 0.0,
            'spectral_rolloff': 0.0,
            'zero_crossing_rate': 0.0,
            'frequency_bands': {'bass': 0, 'mid': 0, 'treble': 0},
            'raw_audio': np.array([])
        }


class DrumMachine:
    """Simple internal drum machine for testing without microphone"""

    def __init__(self, bpm: float = 120):
        self.bpm = bpm
        self.beat_interval = 60.0 / bpm
        self.last_beat_time = time.time()
        self.pattern = [1, 0, 1, 0]  # Simple kick pattern
        self.pattern_index = 0
        self.is_playing = False

        # Generate drum sounds
        self.kick_sound = self._generate_kick()
        self.snare_sound = self._generate_snare()
        self.hihat_sound = self._generate_hihat()

    def _generate_kick(self, duration: float = 0.2, sample_rate: int = 44100) -> np.ndarray:
        """Generate a synthetic kick drum sound"""
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Frequency envelope (starts high, drops quickly)
        freq_env = 60 * np.exp(-t * 30)

        # Amplitude envelope
        amp_env = np.exp(-t * 8)

        # Generate sine wave with frequency modulation
        kick = amp_env * np.sin(2 * np.pi * freq_env * t)

        # Add some noise for texture
        noise = np.random.normal(0, 0.1, len(t)) * amp_env * 0.3

        return kick + noise

    def _generate_snare(self, duration: float = 0.15, sample_rate: int = 44100) -> np.ndarray:
        """Generate a synthetic snare drum sound"""
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Amplitude envelope
        amp_env = np.exp(-t * 15)

        # Tonal component (200Hz)
        tonal = 0.3 * np.sin(2 * np.pi * 200 * t)

        # Noise component
        noise = np.random.normal(0, 1, len(t)) * 0.7

        return amp_env * (tonal + noise)

    def _generate_hihat(self, duration: float = 0.1, sample_rate: int = 44100) -> np.ndarray:
        """Generate a synthetic hi-hat sound"""
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Sharp decay
        amp_env = np.exp(-t * 40)

        # High frequency noise
        noise = np.random.normal(0, 1, len(t))

        # High-pass filter effect (emphasize high frequencies)
        hihat = noise * amp_env

        return hihat * 0.5

    def get_current_audio(self) -> Tuple[np.ndarray, Dict]:
        """Get current drum machine output and features"""
        current_time = time.time()

        if not self.is_playing:
            return np.zeros(1024), {'amplitude': 0, 'beat_detected': False, 'frequency': 0}

        # Check if it's time for next beat
        if current_time - self.last_beat_time >= self.beat_interval:
            self.last_beat_time = current_time
            self.pattern_index = (self.pattern_index + 1) % len(self.pattern)

        # Generate audio based on current pattern
        beat_active = self.pattern[self.pattern_index]
        time_since_beat = current_time - self.last_beat_time

        if beat_active and time_since_beat < 0.2:
            # Generate kick drum
            progress = time_since_beat / 0.2
            audio_data = self.kick_sound[:1024] * (1 - progress)

            features = {
                'amplitude': float(np.max(np.abs(audio_data))),
                'beat_detected': time_since_beat < 0.05,
                'frequency': 60.0,
                'rms': float(np.sqrt(np.mean(audio_data ** 2)))
            }
        else:
            audio_data = np.zeros(1024)
            features = {'amplitude': 0, 'beat_detected': False, 'frequency': 0, 'rms': 0}

        return audio_data, features

    def start(self):
        """Start the drum machine"""
        self.is_playing = True
        self.last_beat_time = time.time()

    def stop(self):
        """Stop the drum machine"""
        self.is_playing = False

    def set_bpm(self, bpm: float):
        """Change the tempo"""
        self.bpm = bpm
        self.beat_interval = 60.0 / bpm

    def set_pattern(self, pattern: List[int]):
        """Set a new drum pattern"""
        self.pattern = pattern
        self.pattern_index = 0


class AudioSmoother:
    """Smooth audio features to reduce jitter"""

    def __init__(self, smoothing_factor: float = 0.8):
        self.smoothing_factor = smoothing_factor
        self.smoothed_values = {}

    def smooth(self, features: Dict) -> Dict:
        """Apply exponential smoothing to audio features"""
        smoothed = {}

        for key, value in features.items():
            if isinstance(value, (int, float)):
                if key not in self.smoothed_values:
                    self.smoothed_values[key] = value
                else:
                    self.smoothed_values[key] = (
                        self.smoothing_factor * self.smoothed_values[key] +
                        (1 - self.smoothing_factor) * value
                    )
                smoothed[key] = self.smoothed_values[key]
            else:
                smoothed[key] = value

        return smoothed


def normalize_audio_features(features: Dict, max_amplitude: float = 1.0) -> Dict:
    """Normalize audio features to standard ranges"""
    normalized = features.copy()

    # Normalize amplitude to 0-1
    if 'amplitude' in normalized:
        normalized['amplitude'] = min(1.0, normalized['amplitude'] / max_amplitude)

    # Normalize RMS to 0-1
    if 'rms' in normalized:
        normalized['rms'] = min(1.0, normalized['rms'] / (max_amplitude * 0.707))

    # Normalize frequency to 0-1 (assuming max 20kHz)
    if 'dominant_frequency' in normalized:
        normalized['dominant_frequency'] = min(1.0, normalized['dominant_frequency'] / 20000.0)

    return normalized


def create_audio_visualizer_data(features: Dict, history_length: int = 100) -> Dict:
    """Create data suitable for audio visualization"""
    if not hasattr(create_audio_visualizer_data, 'history'):
        create_audio_visualizer_data.history = {
            'amplitude': deque(maxlen=history_length),
            'frequency': deque(maxlen=history_length),
            'beats': deque(maxlen=history_length)
        }

    history = create_audio_visualizer_data.history

    # Add current values to history
    history['amplitude'].append(features.get('amplitude', 0))
    history['frequency'].append(features.get('dominant_frequency', 0))
    history['beats'].append(1 if features.get('beat_detected', False) else 0)

    return {
        'amplitude_history': list(history['amplitude']),
        'frequency_history': list(history['frequency']),
        'beat_history': list(history['beats']),
        'current_amplitude': features.get('amplitude', 0),
        'current_frequency': features.get('dominant_frequency', 0),
        'beat_detected': features.get('beat_detected', False)
    }
