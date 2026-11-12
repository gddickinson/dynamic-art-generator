"""The audio features the desktop app (main.AudioProcessor) gives the plugins for one chunk of samples.

numpy only, so the web app and the tests can use exactly what the desktop computes:
  amplitude      RMS of the chunk (desktop definition)
  beat_detected  AudioAnalyzer.detect_beat: chunk energy above the running average of the last 20 chunks plus
                 1.5 standard deviations, at most one beat per 0.1 s (False without an analyzer)
  frequency      peak of |rfft| of the raw chunk, Hz
  raw_data       copy of the chunk
plus every AudioAnalyzer.analyze_audio key the plugins read (dominant_frequency, frequency_bands, spectral_centroid,
onset_detected, estimated_tempo, harmonicity, spectral_rolloff, zero_crossing_rate, rms) when an analyzer is given.
"""
import numpy as np

def desktop_audio_features(audio_data, sample_rate, analyzer=None):
    audio_data = np.asarray(audio_data)
    features = dict(analyzer.analyze_audio(audio_data)) if analyzer is not None else {}
    features.pop("raw_audio", None)
    amplitude = float(np.sqrt(np.mean(audio_data ** 2))) if len(audio_data) else 0.0
    frequency = 0.0
    if len(audio_data) > 0:
        fft = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1 / sample_rate)
        frequency = float(freqs[np.argmax(np.abs(fft))])
    features.update({
        "amplitude": amplitude,
        "beat_detected": bool(features.get("beat_detected", False)),
        "frequency": frequency,
        "raw_data": audio_data.copy(),
    })
    return features
