"""Web interface for the Dynamic Art Generator (FastAPI + plain ES-module front end; the art runs in the browser).

Contents:
  app.py             FastAPI app: static front end, /api/info, /plugins, /presets, /audio_reference
  plugin_catalog.py  catalogue of the Python plugins (headless pygame) + set_parameter cases for the JS-port tests
  demo_signal.py     built-in demo signal (DrumMachine sounds + gliding tone), ported to static/demo_signal.js
  audio_reference.py the repo's audio feature extraction on the demo signal (fixtures and the Verify page)
  static/            front end: pages, pygame-like canvas layer, audio analysis port, plugins/ (JS ports)
"""
