"""Regenerate the Python-vs-JS fixtures in tests/fixtures/ from the repo's own code.

  plugin_cases.json     catalogue of plugins/*.py (names, defaults) + get_parameters() after set_parameter() cases
  audio_reference.json  AudioAnalyzer / desktop features on the built-in demo signal (web/demo_signal.py)

Run: python scripts/make_fixtures.py   (tests/test_web.py checks the committed files are still current)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
FIXTURES = ROOT / "tests" / "fixtures"


def plugin_cases():
    from web.plugin_catalog import catalog, set_cases
    return {"catalog": catalog(), "set_cases": set_cases()}


def audio_reference():
    from web.audio_reference import reference
    return reference()


def main():
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for name, fn in (("plugin_cases.json", plugin_cases), ("audio_reference.json", audio_reference)):
        (FIXTURES / name).write_text(json.dumps(fn(), indent=1, allow_nan=False) + "\n")
        print("wrote", FIXTURES / name)


if __name__ == "__main__":
    main()
