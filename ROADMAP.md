# Dynamic Art Generator — Roadmap

## Current State
A real-time audiovisual art generator with a mature plugin architecture. ~14,200 lines across ~25 Python files. Has 13 art plugins (pendulum, particles, ecosystem, quantum_jazz, cosmic_web, neural_flow, rehoboam, etc.), audio processing, a Tkinter GUI, preset system, and config management. Well-structured with `plugins/`, `utils/`, `presets/`, and `exports/` directories. Several plugins exceed 800 lines. `main.py` is 934 lines.

## Short-term Improvements
- [ ] Split `main.py` (934 lines) into `app.py` (application controller), `gui.py` (Tkinter UI), and `audio_processor.py` (audio pipeline)
- [ ] Split large plugins: `ecosystem.py` (1,201 lines) and `quantum_jazz.py` (957 lines) each need sub-modules or helper files
- [ ] Add type hints to the `ArtPlugin` base class and all plugin interfaces
- [ ] Add plugin validation at load time — check that required methods exist and have correct signatures
- [ ] Add error handling for audio device failures (microphone disconnection mid-session)
- [ ] Add `--list-plugins` CLI flag to show available plugins without launching the GUI
- [ ] Write smoke tests for each plugin: instantiate, call update/render with mock audio, verify no crash

## Feature Enhancements
- [ ] Add video recording: capture the canvas to MP4 in real-time using ffmpeg subprocess
- [ ] Add MIDI input support for controlling parameters with physical controllers
- [ ] Add a plugin parameter preset browser — save/load named parameter sets per plugin
- [ ] Add multi-plugin layering — render two or more plugins simultaneously with blend modes
- [ ] Add fullscreen mode and projector-friendly output for live performance
- [ ] Add audio file playback as input source (not just microphone)
- [ ] Add a waveform/spectrum visualizer overlay that can be toggled on any plugin

## Long-term Vision
- [ ] Port rendering from Pygame+Tkinter to a GPU-accelerated backend (ModernGL or Pyglet) for higher FPS
- [ ] Add OSC (Open Sound Control) protocol support for integration with Ableton Live, TouchDesigner
- [ ] Create a web-based remote control interface (Flask + WebSocket) for mobile parameter tweaking
- [ ] Add a plugin marketplace/registry — allow users to install plugins from a URL
- [ ] Implement a timeline/sequencer for scripted art performances (plugin transitions, parameter automation)
- [ ] Add Syphon/Spout output for routing video to other applications (VJ software, OBS)

## Technical Debt
- [ ] `plugins/particles.py` (697 lines) and `plugins/particle_fountain.py` (695 lines) share particle physics code — extract a shared `particle_base.py`
- [ ] `test_script_macos.py` (697 lines) is unusually large for a test — likely an integration test that should be split
- [ ] `plugin_template.py` exists but plugins don't consistently follow it — enforce interface compliance
- [ ] `config.json` and `example_presets.json` schema is undocumented — add a schema or validation
- [ ] Audio processing likely runs on the main thread — verify and move to a dedicated thread if needed
- [ ] No CI/CD — add linting and import-check workflows
