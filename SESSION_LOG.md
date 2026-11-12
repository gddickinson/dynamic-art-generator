# Session log

## 2026-11-11: web interface and static site (branch `web-interface`)
- Added `web/` (FastAPI + ES modules), `run_web.py` (port 8112), static build, Pages workflow, tests, README section.
- The static site is the working app: JS ports of all 13 plugins on a pygame-like canvas layer (`web/static/pg.js`) and of
  the audio analysis (AudioAnalyzer + desktop features), with demo signal / audio file / microphone / simulated input,
  plugin switching, parameters, example presets and PNG snapshots. All plugins run at 60 fps in Chrome.
- Agreement: audio features JS vs Python on the demo signal, 240 chunks × 16 values, max relative difference 1.5e-12;
  plugin default parameters and 370 `set_parameter` cases identical to Python.
- Bugs fixed in existing code (separate commits, each with a regression test): desktop AudioProcessor did not provide
  `dominant_frequency`/`frequency_bands` that every plugin reads; Particles crash at particle_life 0; Bio-Mechanical
  Garden (vines never shown, network lines misplaced, bright gears skipped); left/up lines missing in Cosmic Web, Noise
  Sphere, Neural Flow, Quantum Jazz; Quantum Jazz crash at creation rate 0; Space Junk spinning 57× too fast (degrees
  as radians); Rehoboam rings piling up on reset; Ecosystem predators always sprinting; parameters with no effect wired
  (flock radii/speed, fountain gravity/wind, cosmic gravity, biomech servo, neural clustering/breathing, ecosystem
  sensitivity/aggression); README corrected.
- Needs George's decision: desktop beat = RMS > 0.1 (constant beats on loud music) vs AudioAnalyzer adaptive beats;
  unwired parameters (cosmic beat_amplification/color_variance, biomech enable_particle_effects, fountain
  turbulence/fade_trails, quantum quantum_coherence_time/beat_observation_strength, noise_sphere beat_sensitivity);
  Ecosystem prey hue overwrites the audio hue shift; fountain wind_force scale (0.15 × value) chosen by us.

## 2026-11-11 (follow-up, George: "fix any other problems")
- Desktop beat detection is now adaptive (AudioAnalyzer.detect_beat: energy above the 20-chunk running average + 1.5
  std, 0.1 s refractory) instead of RMS > 0.1; same code path in Python and JS. Demo: 5 beats in 5.6 s instead of 240/240.
- Last dead parameters: wired Cosmic Web beat_amplification, Particle Fountain turbulence, Quantum Jazz
  quantum_coherence_time (now the documented 5 s, was hard-coded 2 s) and beat_observation_strength, Noise Sphere
  beat_sensitivity; removed Cosmic Web color_variance, Bio-Mechanical Garden enable_particle_effects, Particle Fountain
  fade_trails (nothing to control). 148 -> 145 parameters.
- Musical Ecosystem prey hue now follows the audio (age hue + frequency/amplitude shift, like the predators).
- Still open for George: the Particle Fountain wind_force scale (0.15 x value) is our choice.
