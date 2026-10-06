# nanoMuse v0.1.37-fork.1 — sanitized fork release

Tracking upstream [`v0.1.37`](https://github.com/nano-muse/nanoMuse/releases/tag/v0.1.37) ("Weave").

| | |
|---|---|
| Upstream release | https://github.com/nano-muse/nanoMuse/releases/tag/v0.1.37 |
| Upstream tag commit | `10a699280e02827cdae5c81ca1093cda1dea5208` |
| **Sanitized fork commit** | **`ac5877f86d71ce157b408d6c977c1243ff65837d`** (merge of PR #11 on fork/main) |
| Fork tag | `v0.1.37-fork.1` (annotated) on the sanitized commit — **never** the raw upstream commit |
| Merged fork PR | https://github.com/zeeshanhaque21/nanoMuse/pull/11 |
| Also tracks | v0.1.36, v0.1.35 (same sanitized commit) |

## Assets

| File | Size | SHA-256 |
|---|---|---|
| `nanoMuse-0.1.37-arm64.apk` | 33,626,874 bytes | `93dc51204fac1c1c6406c957ed76f19e8c85d15c657041832673471d11dae41e` |
| `nanoMuse-0.1.37-arm64.apk.sha256` | — | the checksum above |

The APK was built from the tagged commit on this machine (`./gradlew :app:assembleRelease`).
**Upstream binary assets are never copied** — they may still contain the `.cn` backend and omit
every fork-only change below.

### APK verification actually performed

| Check | Result |
|---|---|
| Signature | `CN=nanoMuse fork, OU=release, O=nanoMuse fork` — a real release key, **not** `CN=Android Debug` |
| Signer SHA-256 | `811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` — the **same key** as `v0.1.34-fork.1`, so this build updates an installed copy |
| Badging | `io.github.nanomuse.app`, `versionName=0.1.37`, `versionCode=38`, `arm64-v8a` |
| `.cn` scan of the **signed** APK | **0 files** with `nanomuse.cn` across all 592 entries; `classes.dex`, `resources.arsc`, `AndroidManifest.xml` all clean |
| Upstream release refs in the dex | **0** — all three mobile updaters read this fork's releases |
| Checksum | `shasum -a 256` → recorded in the `.sha256` asset |

The scan was run against the **signed artifact**, not the source tree, because the shipped APK is
what a phone actually receives. That mattered: a source-only grep missed a second Android updater
(`com/openminis/app/data/UpdateChecker.kt`) that still polled upstream's releases.

## Fork changes on top of upstream

PR #11 merged upstream v0.1.34 → v0.1.37 and removed every active reference to the unwanted
`nanomuse.cn` backend.

**The backend contract:** the fork never contacts, links to, or defaults to `nanomuse.cn` or any
`.cn` cloud backend. Defaults are empty and the operator configures their own relay via
`NANOMUSE_CLOUD_BASE_URL` / `cloud.base_url`. Where a required default was removed, the app raises a
clear configuration error **before** any network I/O.

Sanitized at the owning configuration layer, never by global replacement:

| Surface | After |
|---|---|
| `nanomuse/server/update.py` | this fork's GitHub releases first; mirror **opt-in** via `NANOMUSE_UPDATE_INDEX_URL`, empty by default |
| `harness/…/src/desk.ts` | GitHub first, `RELEASES_INDEX = ''`, optional configured mirror retained |
| `harness/…/src/nudges.ts` | `NUDGES_ORIGIN = ''` — the feature stays off until a relay is configured |
| Android `community/UpdateCheck.kt` | fork releases; `INDEX_URL = ""` **guarded**, so no empty-URL request |
| Android `com/openminis/app/data/UpdateChecker.kt` | fork releases (a second, separate updater) |
| iOS `NanoMuseUpdateCheck.swift` | fork releases; `indexURL` guarded |
| iOS `NanoMuseSettings.swift` | privacy link points at this fork's tracked `docs/privacy.md`, never force-unwrapped empty |
| web + desktop download links | the fork's releases page |

Upstream features kept and verified **wired**, not merely present: `CloudSettings.sync`, the console
conversation-sync card with its i18n keys in both languages, the desktop `SyncControls` at both call
sites, and upstream's new sync/one-thread documentation.

Fork-only features preserved: Google Calendar, vault-backed MCP headers, configurable relay hosting,
signed-out relay editing, bundled desktop Playwright/Chromium, and the private relay override.

## Checks on the tagged commit

| Check | Result |
|---|---|
| CI `Ruff lint` / `Ruff format` | **pass** |
| CI `Mypy` | **pass** — no issues in 128 source files |
| CI `Tests` | **pass** (matrix: ubuntu py3.11/3.12/3.13, macOS, Windows) |
| CI `web app build` — eslint, vitest, tsc, "Built app is committed" | **pass** |
| CI `Android` debug APK arm64-v8a, `docker build`, `harness bundle`, `gateway tests` | **pass** |
| CI `Commits` — DCO sign-off, Conventional Commit subjects | **pass** |
| **Total CI on the tested head** | **15 checks, all pass, 0 failures** |
| Local `cloud/tests` | **91 passed** |
| Local `demo/showcase/gateway/tests` | **40 passed** |
| Local web `npm run check` | **pass** — tsc clean, 51 tests |
| Local harness `tsc` + `node --test` | **pass** — 132 tests |

### Pre-existing failures, proven not regressions

`pytest -m "not live"` reports 4 failures on **pristine upstream `v0.1.37`** and the identical 4
after this merge (`test_config` ×2, `test_memory_goals`, `test_skills`) — all environment-sensitive
(vault placeholder resolution, PST/PDT timezone, a glob). Verified by running the identical command
on the upstream commit, on the pre-review fork head, and on the merged head. **No failure is unique
to this fork.**

## Review

A **separate fresh-context adversarial review** audited the diff and returned *mergeable after
fixes*. Both major findings were real and are fixed in this release:

1. The emptied mirror index was still fetched unconditionally on Android and iOS — caught by
   `Request.Builder().url("")` throwing (swallowed, so no crash, but a guaranteed-to-fail request on
   every check). Both now guard, matching the runtime and harness.
2. The mobile version lookup still read **upstream's** releases while the download button pointed at
   the fork. Both now read this fork. A follow-up scan of the built dex found a **third** updater with
   the same problem, also fixed.

The regression test now walks the entire Android and iOS source tree rather than listing files, so a
fourth updater cannot slip in behind named checks.

## Honest platform limitations

- **macOS and Windows desktop builds are not attached.** The fork has **zero GitHub Actions secrets**,
  so no signed or notarized macOS or Windows artifact is possible here. Release those yourself from
  the tagged commit.
- **iOS is not attached.** No sideload path on this host, and the Xcode build needs two prebuilt
  native inputs (`ProviderCustomization.xcconfig`, `Rclone.xcframework`) that are git-ignored and not
  present. Swift sources were verified with `swiftc -parse` (clean), which is a parse check, not a
  device build.
- **The APK signing key is the app's permanent identity.** If it is lost, no future APK can update an
  installed copy, because Android requires the same signing key for every update. The key is stored
  outside this repository at `android/nanomuse-release.jks` (git-ignored); back it up.
- Remaining `.cn` strings inside the APK are third-party bring-your-own-key model providers in the
  bundled `libgojni.so` (ModelScope, MiniMax, Moonshot, SiliconFlow, iFlytek, Ark, TBox, SCNet) —
  not the nanoMuse backend, and not contacted without the user's own key.

## Historical references, preserved not rewritten

`CHANGELOG.md`, `docs/releases/**`, `docs/readme/**`, `cloud/deploy/nanomuse-hk/**`, `demo/**`,
`docs/privacy.md`, `docs/roadmap.md`, `site/README.md` and `README.md`'s release history still mention
upstream's host. Those are attribution and history; they were reported, not edited.

🤖 Generated with [Claude Code](https://claude.com/claude-code)