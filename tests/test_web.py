"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific ---------------------------------------------------------------------------------------------
import json  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"


def _close(a, b, path=""):
    """Numbers equal within rtol 1e-9 (libm differs across platforms); everything else exactly."""
    if isinstance(b, bool) or not isinstance(b, (int, float)):
        if isinstance(b, dict):
            assert set(a) == set(b), path
            for k in b:
                _close(a[k], b[k], f"{path}.{k}")
        elif isinstance(b, list):
            assert len(a) == len(b), path
            for i, (x, y) in enumerate(zip(a, b)):
                _close(x, y, f"{path}[{i}]")
        else:
            assert a == b, path
    else:
        assert a == pytest.approx(b, rel=1e-9, abs=1e-12), path


def test_plugins_endpoint_lists_every_plugin_file():
    names = [p["source"] for p in client.get("/api/plugins").json()]
    files = sorted("plugins/" + f.name for f in (ROOT / "plugins").glob("*.py") if f.name != "__init__.py")
    assert sorted(names) == files


def test_every_plugin_has_a_js_port():
    reg = (STATIC / "plugins" / "index.js").read_text()
    for p in client.get("/api/plugins").json():
        assert f"'{p['name']}'" in reg, p["name"]


def test_info_counts():
    info = client.get("/api/info").json()
    assert info["plugins"] == 13 and info["presets"] == 12 and info["chunk_size"] == 1024


def test_presets_name_existing_plugins():
    names = {p["name"] for p in client.get("/api/plugins").json()}
    for p in client.get("/api/presets").json()["presets"]:
        assert p["plugin"] in names, p["name"]


def test_fixtures_current():
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_fixtures
    _close(make_fixtures.plugin_cases(), json.loads((FIXTURES / "plugin_cases.json").read_text()), "plugin_cases")
    _close(make_fixtures.audio_reference(), json.loads((FIXTURES / "audio_reference.json").read_text()), "audio")


def test_files_under_500_lines():
    for f in list((ROOT / "web").rglob("*.py")) + list(STATIC.rglob("*.js")) + list(STATIC.glob("*.mjs")):
        assert len(f.read_text().splitlines()) < 500, f
