"""Catalogue of the real Python plugins (plugins/*.py) for the web API and the JS-port fixtures.

Imports pygame headless (SDL dummy drivers) because every plugin module imports it; no window is opened.
`catalog()` lists each plugin's name, description, version, source file and default parameters (from its own
get_parameters()); `set_cases()` records what set_parameter() leaves in get_parameters() for a few values, which the
node test of the JS ports compares against.
"""
import inspect
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SURFACE_SIZE = (800, 600)   # config.json application.canvas_size, the size main.py gives every plugin
FIRST = "Pendulum"          # config.json plugins.default_plugin


def plugin_classes():
    """{PLUGIN_NAME: class} from the repo's own PluginManager, default plugin first, then alphabetical."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plugins = _quiet(__import__, "plugins")
    classes = dict(plugins.plugin_manager.plugin_classes)
    return dict(sorted(classes.items(), key=lambda kv: (kv[0] != FIRST, kv[0])))


def _quiet(fn, *a):
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a)


def catalog():
    out = []
    for name, cls in plugin_classes().items():
        inst = _quiet(cls, SURFACE_SIZE)
        params = inst.get_parameters()
        out.append({
            "name": name,
            "class": cls.__name__,
            "description": getattr(cls, "PLUGIN_DESCRIPTION", ""),
            "version": getattr(cls, "PLUGIN_VERSION", ""),
            "source": "plugins/" + Path(inspect.getfile(cls)).name,
            "doc": inspect.cleandoc(cls.__doc__ or "").split("\n\n")[0],
            "parameters": params,
        })
    return out


def set_values(default):
    """Values the desktop sliders can send for a parameter (Tk DoubleVar floats in 0..2*default)."""
    if isinstance(default, bool):
        return [not default]
    return [float(default) * 2, float(default) * 0.37, 0.0]


def set_cases():
    """For every plugin and parameter: get_parameters() after set_parameter(name, v) on a fresh instance.

    `after` keeps the parameter itself plus every entry that differs from the defaults (the rest are unchanged)."""
    cases = []
    for name, cls in plugin_classes().items():
        defaults = _quiet(cls, SURFACE_SIZE).get_parameters()
        for key, default in defaults.items():
            for v in set_values(default):
                inst = _quiet(cls, SURFACE_SIZE)
                _quiet(inst.set_parameter, key, v)
                after = inst.get_parameters()
                diff = {k: x for k, x in after.items() if k == key or defaults.get(k) != x}
                cases.append({"plugin": name, "param": key, "value": v, "after": diff})
    return cases
