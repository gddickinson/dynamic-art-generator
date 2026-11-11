# Dynamic Art Generator

Audio-reactive art: `main.py` (Tkinter + pygame desktop app), plugins in `plugins/`, audio analysis in `utils/`,
web interface and static GitHub Pages site in `web/` (JS ports of every plugin and of the audio analysis).

@INTERFACE.md

- Tests: `python -m pytest -q tests` (plugin regression tests need pygame; `tests/test_web.py` also runs the node tests).
- After changing a plugin or the audio analysis in Python, mirror it in `web/static/` and run
  `python scripts/make_fixtures.py` (fixtures in `tests/fixtures/` are checked for currency).
- Keep files under 500 lines (several original modules are already over; split them when you touch them).
