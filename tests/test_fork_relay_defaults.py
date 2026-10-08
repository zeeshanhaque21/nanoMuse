"""Fork regression: no default relay to the unwanted backend; custom relay honored.

Covers debug and release paths at the configuration layer (no network):
- Python runtime defaults to empty (no nanomuse.cn); custom base passes through.
- Empty relay raises relay_unconfigured from _request without network I/O.
- Desktop sources and relay-package defaults contain no nanomuse.cn (file-level check).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from nanomuse.cloud import CloudClient, CloudError
from nanomuse.config import CloudSettings

CUSTOM = "https://relay.example.net"
ROOT = Path(__file__).resolve().parents[1]


def test_no_default_cloud_backend_in_runtime() -> None:
    assert CloudSettings().base_url == ""
    assert CloudSettings().required is False


def test_custom_relay_preserved_verbatim() -> None:
    assert CloudSettings(base_url=CUSTOM).base_url == CUSTOM
    assert CloudClient(CUSTOM).base_url == CUSTOM


def test_empty_relay_fails_clear_without_network() -> None:
    async def go() -> None:
        await CloudClient("")._request("GET", "/v1/me")

    with pytest.raises(CloudError) as exc:
        asyncio.run(go())
    assert exc.value.code == "relay_unconfigured"
    assert "NANOMUSE_CLOUD_BASE_URL" in exc.value.message


@pytest.mark.parametrize("tree", ["harness/desktop/src", "harness/dsh-nanomuse/src"])
def test_desktop_sources_have_no_unwanted_backend(tree: str) -> None:
    for path in (ROOT / tree).rglob("*"):
        if path.is_file() and path.suffix in {".ts", ".tsx", ".mjs", ".js"}:
            assert "nanomuse.cn" not in path.read_text(encoding="utf-8"), path


def test_relay_package_defaults_have_no_unwanted_backend() -> None:
    text = (ROOT / "cloud" / "nanomuse_cloud" / "config.py").read_text(encoding="utf-8")
    assert "nanomuse.cn" not in text
