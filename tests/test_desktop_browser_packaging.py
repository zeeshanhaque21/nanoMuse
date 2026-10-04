"""Browser bundles must retain framework symlinks when copied into the runtime."""

import runpy
from pathlib import Path
from types import SimpleNamespace


def test_runtime_copies_browser_bundle_intact(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[1] / "scripts/desktop-app/build-runtime.py"
    build = runpy.run_path(str(script))["build"]
    globals_ = build.__globals__
    dist = tmp_path / "dist"
    built = dist / "nanomuse"
    built.mkdir(parents=True)
    (built / "nanomuse").write_text("fake executable")
    package = tmp_path / "playwright"
    browsers = package / "driver/package/.local-browsers"
    browsers.mkdir(parents=True)
    (browsers / "framework").write_text("framework content")
    (browsers / "framework-link").symlink_to("framework")
    monkeypatch.setitem(globals_, "DIST", dist)
    monkeypatch.setitem(globals_, "run", lambda *args, **kwargs: None)
    # The fake build output already exists; suppress only the pre-build cleanup.
    real_rmtree = globals_["shutil"].rmtree
    monkeypatch.setattr(
        globals_["shutil"],
        "rmtree",
        lambda path, **kwargs: None if path == dist else real_rmtree(path, **kwargs),
    )
    monkeypatch.setattr(
        globals_["importlib"].util,
        "find_spec",
        lambda name: SimpleNamespace(origin=str(package / "__init__.py")),
    )
    target = tmp_path / "runtime"
    assert build(target) == target / "nanomuse"
    copied = target / "_internal/playwright/driver/package/.local-browsers"
    assert (copied / "framework-link").is_symlink()
    assert (copied / "framework-link").read_text() == "framework content"
