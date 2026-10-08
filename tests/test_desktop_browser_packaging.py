"""Browser bundles must retain framework symlinks when copied into the runtime."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def test_runtime_copies_browser_bundle_intact(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[1] / "scripts/desktop-app/build-runtime.py"
    build = runpy.run_path(str(script))["build"]
    globals_ = build.__globals__
    dist = tmp_path / "dist"
    built = dist / "nanomuse"
    built.mkdir(parents=True)
    # build-runtime.py looks for nanomuse.exe on win32 and returns that path, so the fixture
    # has to create and expect the platform's own name
    exe_name = "nanomuse.exe" if sys.platform == "win32" else "nanomuse"
    (built / exe_name).write_text("fake executable")
    (built / "runtime-framework").write_text("runtime framework content")
    (built / "runtime-framework-link").symlink_to("runtime-framework")
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
    assert build(target) == target / exe_name
    assert (target / "runtime-framework-link").is_symlink()
    assert (target / "runtime-framework-link").read_text() == "runtime framework content"
    copied = target / "_internal/playwright/driver/package/.local-browsers"
    assert (copied / "framework-link").is_symlink()
    assert (copied / "framework-link").read_text() == "framework content"
