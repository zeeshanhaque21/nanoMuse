"""Fork regression: post-0.1.37 sanitization of upstream's new code.

Upstream 0.1.35-0.1.37 added code that reached the unwanted backend without conflicting
with the fork, so it auto-merged in. Each surface below was checked at its owning layer:

- runtime release check: GitHub first, mirror only when NANOMUSE_UPDATE_INDEX_URL is set
- Android/iOS update check index constants default to empty
- web + desktop download links point at the fork's releases
- the desktop nudges origin defaults to empty (feature off until configured)
- the iOS privacy URL is the fork's tracked doc, never a force-unwrapped empty string
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from nanomuse.server import update

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_update_check_has_no_default_mirror_and_no_cn_host() -> None:
    """The release check must never reach a third-party host unless configured."""
    text = _read("nanomuse/server/update.py")
    assert "nanomuse.cn" not in text
    # the mirror is opt-in and env-derived; the fork repo is the primary source
    assert 'os.environ.get("NANOMUSE_UPDATE_INDEX_URL", "")' in text
    assert 'FORK_REPO = "zeeshanhaque21/nanoMuse"' in text


def test_update_check_default_index_is_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Import-time default is empty; a configured mirror is honored verbatim."""
    monkeypatch.delenv("NANOMUSE_UPDATE_INDEX_URL", raising=False)
    assert update.latest_from_index({"releases": [{"tag": "v0.1.40"}]}) == "v0.1.40"
    # the module constant is only non-empty when an operator set it
    assert update.DOWNLOAD_PAGE.startswith("https://github.com/zeeshanhaque21/nanoMuse")
    assert update.RELEASES_API.startswith("https://api.github.com/repos/zeeshanhaque21/nanoMuse")
    assert os.environ.get("NANOMUSE_UPDATE_INDEX_URL", "") == ""


@pytest.mark.parametrize(
    "rel",
    [
        "android/src/android/app/src/main/java/io/github/nanomuse/community/UpdateCheck.kt",
        "android/src/ios/NanoMuse/NanoMuseUpdateCheck.swift",
        "android/src/ios/NanoMuse/NanoMuseSettings.swift",
        "android/src/ios/NanoMuse/NanoMuseVideoGen.swift",
        "harness/dsh-nanomuse/src/client/DevicesPanel.tsx",
        "harness/dsh-nanomuse/src/nudges.ts",
        "harness/dsh-nanomuse/src/video.ts",
        "nanomuse/server/api.py",
        "web/src/screens/DevicesScreen.tsx",
        "web/src/screens/SettingsScreen.tsx",
        "web/src/types.ts",
    ],
)
def test_no_active_client_source_reaches_the_unwanted_backend(rel: str) -> None:
    assert "nanomuse.cn" not in _read(rel)


def test_download_links_point_at_the_fork_releases() -> None:
    for rel, needle in (
        ("web/src/screens/DevicesScreen.tsx", "github.com/zeeshanhaque21/nanoMuse/releases"),
        (
            "harness/dsh-nanomuse/src/client/DevicesPanel.tsx",
            "github.com/zeeshanhaque21/nanoMuse/releases",
        ),
        (
            "android/src/android/app/src/main/java/io/github/nanomuse/community/UpdateCheck.kt",
            "github.com/zeeshanhaque21/nanoMuse/releases",
        ),
    ):
        assert needle in _read(rel), rel


def test_android_update_check_index_default_is_empty() -> None:
    text = _read(
        "android/src/android/app/src/main/java/io/github/nanomuse/community/UpdateCheck.kt"
    )
    assert 'const val INDEX_URL = ""' in text
    assert 'const val DOWNLOAD_URL = "https://nanomuse.cn/dl/"' not in text


def test_ios_update_check_index_default_is_empty() -> None:
    text = _read("android/src/ios/NanoMuse/NanoMuseUpdateCheck.swift")
    assert 'indexURL = ""' in text


def test_ios_privacy_link_is_safe_when_unset() -> None:
    """A force-unwrapped empty URL traps at launch; the fork's doc is a real page."""
    text = _read("android/src/ios/NanoMuse/NanoMuseSettings.swift")
    assert 'URL(string: "")!' not in text
    assert "github.com/zeeshanhaque21/nanoMuse/blob/main/docs/privacy.md" in text


def test_desktop_nudges_origin_is_off_by_default() -> None:
    text = _read("harness/dsh-nanomuse/src/nudges.ts")
    assert "NUDGES_ORIGIN = ''" in text


def test_cloud_sync_default_survives_the_merge() -> None:
    """0.1.36/0.1.37 conversation sync must exist, with the fork's required=False."""
    from nanomuse.config import CloudSettings

    assert CloudSettings().required is False
    assert CloudSettings().base_url == ""
    assert CloudSettings().sync is True
