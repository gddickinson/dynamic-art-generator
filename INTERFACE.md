# Dynamic Art Generator: interface map

## Entry points
| File | Purpose |
|------|---------|
| `main.py` | Desktop app: Tkinter GUI, `AudioProcessor` (PyAudio), plugin discovery, 60 fps update/render loop (`DynamicArtGenerator`) |
| `launcher.py`, `macos_demo.py` | macOS launcher; pygame-only demo with simulated audio features |
| `setup.py`, `test_script_macos.py` | Dependency installer/checker; macOS environment check script |
| `run_web.py` | Web app on http://127.0.0.1:8112 (`web.app:app`) |
| `scripts/build_static.py` | Export the static site to `site/` (every GET in `STATIC_ENDPOINTS` as JSON) |
| `scripts/make_fixtures.py` | Regenerate `tests/fixtures/*.json` from the Python code |
| `scripts/screenshots.py` | Playwright smoke test (`--static` / `--base`) and README images (`--shots` → `docs/img/`) |
| `.github/workflows/pages.yml` | Test, build and publish the static site on push to `main` |

## Python packages
| File | Contents |
|------|----------|
| `plugins/__init__.py` | `ArtPlugin` base class (update/render/get_parameters/set_parameter/reset), `PluginManager` |
| `plugins/*.py` | 13 plugins: pendulum, particles, biomech_garden, cosmic_web, digital_spectre, ecosystem, musical_flock, neural_flow, noise_sphere, particle_fountain, quantum_jazz, rehoboam, space_junk |
| `utils/audio_utils.py` | `AudioAnalyzer` (amplitude, rms, dominant frequency, bands, centroid, beats, onsets, tempo, ...), `DrumMachine`, `AudioSmoother` |
| `utils/desktop_features.py` | `desktop_audio_features()`: what `AudioProcessor` hands the plugins (RMS amplitude, beat = RMS > 0.1, + AudioAnalyzer keys) |
| `utils/math_utils.py` | `Vector2D`, `ColorUtils`, `GeometryUtils` |
| `config.json`, `example_presets.json` | Settings (canvas 800×600, 44.1 kHz, 1024-sample chunks); 12 presets |

## Web: `web/`
| File | Purpose |
|------|---------|
| `app.py` | FastAPI: `/api/info`, `/plugins`, `/presets`, `/audio_reference`; `STATIC_ENDPOINTS` |
| `plugin_catalog.py` | Catalogue of the Python plugins (headless pygame) + `set_parameter` cases |
| `demo_signal.py` | Built-in demo signal: DrumMachine sounds at 120 BPM + tone gliding 240–640 Hz (mulberry32 noise) |
| `audio_reference.py` | `desktop_audio_features` + `AudioAnalyzer` on the demo signal, stream clock |
| `static/index.html`, `style.css` (kit), `style_app.css`, `core.js` (kit), `main.js`, `static_api.js`, `background.js`, `icon.svg` | Shell, theme, router, static data layer |
| `static/pg.js` | pygame-like drawing layer on Canvas 2D (`Gfx`: circle, line, polygon, rect, text, layer, blit, blended) |
| `static/plugin_base.js`, `pyrand.js` | JS `ArtPlugin` base, `hsvToRgb`, clock; seeded random/uniform/randint/choice/gauss |
| `static/plugins/index.js` | Registry of the 13 JS plugin ports (lazy import); one module per plugin + `*_parts`/helper modules |
| `static/audio_analyzer.js`, `fft.js` | Port of `AudioAnalyzer` + `desktop_audio_features`; radix-2 real FFT |
| `static/demo_signal.js`, `audio_feed.js` | Demo signal port; demo/file/mic/simulated sources → features per 1024-sample chunk |
| `static/art_runner.js`, `params_panel.js`, `meters.js` | Fixed 60 Hz update + render loop, PNG snapshot; parameter controls; feature meters |
| `static/home.js`, `studio.js`, `plugins_page.js`, `verify.js`, `about.js` | Pages `#/`, `#/studio`, `#/plugins`, `#/verify`, `#/about` |
| `static/reference.js` | Replays the Python reference run in JS and compares |
| `static/*.test.mjs`, `mock_canvas.mjs` | Node tests (audio vs Python, plugin ports vs Python); mock canvas (not shipped) |

## Tests
| File | Coverage |
|------|----------|
| `tests/test_web.py` | API, static build, node tests, fixtures current, every plugin ported, files < 500 lines (web) |
| `tests/test_desktop_audio_features.py`, `test_particles_zero_life.py`, `test_plugin_fixes_*.py` (+ `plugin_test_utils.py`) | Regression tests for the fixed bugs |

## Data flow
```
Desktop: PyAudio chunk ─ desktop_audio_features ─▶ plugin.update(features, 1/60) ─▶ plugin.render(pygame surface) ─▶ Tk canvas
Web:     AudioFeed (demo/file/mic/sim) ─ audio_analyzer.js ─▶ ArtRunner ─▶ JS plugin.update / render(Gfx) ─▶ <canvas>
         scripts/build_static.py ─▶ site/ (static/ + api/*.json) ─▶ GitHub Pages
```
