"""FastAPI web app for the Dynamic Art Generator: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8112, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below. The art itself
runs in the browser (JS ports of plugins/*.py and of the audio analysis); the API supplies the catalogue of the real
Python plugins, the example presets and the Python reference run used by the Verify page.
"""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .audio_reference import reference, summary
from .plugin_catalog import SURFACE_SIZE, catalog

STATIC = Path(__file__).resolve().parent / "static"
ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="Dynamic Art Generator")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@lru_cache(maxsize=1)
def _catalog():
    return catalog()


@lru_cache(maxsize=1)
def _reference():
    return reference()


def _config():
    return json.loads((ROOT / "config.json").read_text())


@app.get("/api/info")
def info():
    """Project summary for the home page (counts come from the code and config.json)."""
    cfg = _config()
    plugins = _catalog()
    return {
        "title": "Dynamic Art Generator",
        "summary": "A real-time audiovisual art generation system with a plugin-based architecture. "
                   "Create art that responds to music and sound in real-time.",
        "plugins": len(plugins),
        "parameters": sum(len(p["parameters"]) for p in plugins),
        "presets": len(_presets()["presets"]),
        "canvas_size": list(SURFACE_SIZE),
        "sample_rate": cfg["audio"]["sample_rate"],
        "chunk_size": cfg["audio"]["chunk_size"],
        "target_fps": cfg["application"]["target_fps"],
        "version": cfg["application"]["version"],
    }


@app.get("/api/plugins")
def plugins():
    """Every plugin in plugins/*.py: name, description, source file and default parameters (from Python)."""
    return _catalog()


def _presets():
    return json.loads((ROOT / "example_presets.json").read_text())


@app.get("/api/presets")
def presets():
    """example_presets.json: the presets (plugin + parameters) and their categories."""
    d = _presets()
    return {"presets": d["presets"], "categories": d.get("categories", {})}


@app.get("/api/audio_reference")
def audio_reference():
    """The Python feature extraction on the demo signal, chunk by chunk (the Verify page replays it in JS)."""
    ref = _reference()
    return {**ref, "summary": summary(ref["rows"])}


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/plugins", "/presets", "/audio_reference"]
