"""Fork regression: active docs, the website and the Pages site link no upstream backend.

Only links (https URLs) are checked, so attribution text in prose stays. ALLOWED is legal
text pending the owner's decision or a historical process note; HISTORY is release notes.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_LINK = re.compile(
    r"https?://(?:[a-z0-9-]+\.)*nanomuse\.cn\b"
    r"|https?://demo\.nanomuse\.dev\b"
    r"|https?://nano-muse\.github\.io\b"
    r"|https?://(?:www\.)?github\.com/nano-muse/(?!proot\b)"
    r"|https?://api\.github\.com/repos/nano-muse/"
)
ALLOWED = {
    "docs/privacy.md",
    "docs/zh/privacy.md",
    "docs/launch-checklist.md",
    "site/README.md",
}
HISTORY = ("docs/releases/",)
SCANNED = [
    "README.md",
    "CONTRIBUTING.md",
    "cloud/README.md",
    "cloud/.env.example",
    "config/config.example.toml",
    "docs/**/*.md",
    "docs/readme/*.md",
    "website/**/*.mts",
    "website/**/*.vue",
    "website/**/*.ts",
    "site/**/*.html",
    ".github/**/*.yml",
]


def _active_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in SCANNED:
        files.update(p for p in ROOT.glob(pattern) if p.is_file())
    keep = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWED or rel.startswith(HISTORY):
            continue
        keep.append(path)
    return sorted(keep)


@pytest.mark.parametrize("path", _active_files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_active_file_links_no_upstream_backend(path: Path) -> None:
    hits = [
        f"{n}: {m.group(0)}"
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        for m in UPSTREAM_LINK.finditer(line)
    ]
    assert not hits, "\n".join(hits)


def test_the_scan_sees_the_active_docs() -> None:
    names = {p.relative_to(ROOT).as_posix() for p in _active_files()}
    assert {"README.md", "docs/index.md", "website/.vitepress/config.mts", "site/legacy.html"} <= names
