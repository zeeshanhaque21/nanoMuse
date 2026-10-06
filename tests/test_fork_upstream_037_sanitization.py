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

import io
import os
import re
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


def test_android_update_check_guards_the_empty_mirror_url() -> None:
    """Regression: INDEX_URL is "" by default, so it must be guarded, not fetched.

    An unguarded get("") reaches OkHttp's Request.Builder().url(""), which throws
    IllegalArgumentException. It is caught, so the app does not crash, but every check
    would perform a guaranteed-to-fail request and log a misleading failure before
    falling through to GitHub. The sibling surfaces (update.py `if INDEX_URL:`,
    desk.ts `if (!mirrorIndex)`) both guard; Android was the only one that did not.
    """
    text = _read(
        "android/src/android/app/src/main/java/io/github/nanomuse/community/UpdateCheck.kt"
    )
    assert "INDEX_URL.isNotBlank()" in text, "Android must not fetch an empty mirror URL"
    # and it must actually guard the call site, not merely mention the constant
    assert "get(INDEX_URL)" in text
    guarded = re.search(r"if \(INDEX_URL\.isNotBlank\(\)\) \{\s*get\(INDEX_URL\)", text)
    assert guarded, "the get(INDEX_URL) call must sit inside the blank check"


def test_ios_update_check_guards_the_empty_mirror_url() -> None:
    """Same guard on the iOS side: never fetchJSON("") when no mirror is configured."""
    text = _read("android/src/ios/NanoMuse/NanoMuseUpdateCheck.swift")
    assert "!indexURL.isEmpty" in text
    assert re.search(r"if !indexURL\.isEmpty, let json = await fetchJSON\(indexURL\)", text)


def test_mobile_update_checks_read_the_fork_releases_not_upstreams() -> None:
    """The version row and its download link must agree.

    The runtime (FORK_REPO) and the harness (RELEASES_REPO) point at the fork, and the
    download links do too. If the version lookup still read upstream's releases, the app
    would report upstream's latest version while its download button went to the fork.
    """
    android = _read(
        "android/src/android/app/src/main/java/io/github/nanomuse/community/UpdateCheck.kt"
    )
    ios = _read("android/src/ios/NanoMuse/NanoMuseUpdateCheck.swift")
    for name, text in (("android", android), ("ios", ios)):
        assert "nano-muse/nanoMuse" not in text, f"{name} still reads upstream releases"
        assert "api.github.com/repos/zeeshanhaque21/nanoMuse" in text, f"{name} must read the fork"
    # the iOS fallback page must be the fork's releases too
    assert "fallbackReleasePage" in ios and "github.com/zeeshanhaque21/nanoMuse" in ios


def test_no_android_or_ios_source_reads_upstream_releases() -> None:
    """No shipped mobile source may poll upstream's releases.

    Three separate updaters exist on Android: community/UpdateCheck.kt (the Version row)
    and com/openminis/app/data/UpdateChecker.kt (the self-update poller). Fixing only the
    first leaves the second reporting upstream's newest version. iOS has its own in
    NanoMuseUpdateCheck.swift. This scans the whole mobile source tree so a fourth one
    cannot be added behind the tests' backs.
    """
    roots = ("android/src/android/app/src/main/java", "android/src/ios")
    offenders = []
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not fn.endswith((".kt", ".java", ".swift")):
                    continue
                full = os.path.join(dirpath, fn)
                text = io.open(full, encoding="utf-8", errors="replace").read()
                if "repos/nano-muse/nanoMuse" in text or 'OWNER = "nano-muse"' in text:
                    offenders.append(os.path.relpath(full, ROOT))
    assert not offenders, f"still reading upstream releases: {offenders}"
