# nanoMuse v1.0.2-fork.1 — sanitized fork release

Tracking upstream [`v1.0.2`](https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.2) ("Trim").

| | |
|---|---|
| Upstream release | https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.2 |
| Upstream tag commit | `7c91811ef16a34fd575c8614fad2ca754088d763` |
| **Sanitized fork commit** | the sanitized commit this run produced on `fork/main`; its exact SHA is in `completion.md` |
| Fork tag | `v1.0.2-fork.1` (annotated) on the sanitized commit — **never** the raw upstream commit |
| Merged fork PR | this run's PR (see the completion report) |
| Also tracks | `v1.0.1` (Ballast), `v1.0.0` (Keel) — the same sanitized commit |

## Assets

| File | Size | SHA-256 |
|---|---|---|
| `nanoMuse-1.0.2-arm64.apk` | 38,852,775 bytes | `43c3832ed99b7e3cae38cbcc771f5d43197a4c8dd5593100a3d056a1dbb0499e` |
| `nanoMuse-1.0.2-arm64.apk.sha256` | — | the checksum above |

The APK was built from the sanitized commit on this machine
(`scripts/release-apk.sh 1.0.2` → `./gradlew :app:assembleRelease`).
**Upstream binary assets are never copied** — they may still contain the `.cn` backend and
omit every fork-only change below.

### APK verification actually performed

| Check | Result |
|---|---|
| Signature | `CN=nanoMuse fork, OU=release, O=nanoMuse fork` — a real release key, **not** `CN=Android Debug` |
| Signer SHA-256 | `811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` — the **same key** as `v0.1.34-fork.1`, so this build updates an installed copy |
| Badging | `io.github.nanomuse.app`, `versionName=1.0.2`, `versionCode=45`, `arm64-v8a` |
| Checksum | `shasum -a 256` → recorded in the `.sha256` asset |

## Sanitization

The canonical scan (`maintenance/RUNBOOK.md`) leaves only 13 files, every one classified:
attribution prose (`docs/zh/cloud.md`, `docs/zh/every-device.md`), legal text
(`docs/zh/privacy.md`), a deploy-artifact filename (`cloud/README.md`), immutable prior-run
evidence, this runbook, and three absence-assertion tests. The active surfaces
(`nanomuse/`, `web/src/`, `cloud/nanomuse_cloud/`, `harness/*/src/`, `android/src/`,
`nanomuse/server/static/`) carry **no** `nanomuse.cn`.

The relay seam is `cloud.base_url` / `NANOMUSE_CLOUD_BASE_URL` only; there is no default
relay, and an empty relay raises `relay_unconfigured` before any network I/O.

## Fork-only changes kept

Google Calendar; vault-backed MCP headers; configurable relay hosting; signed-out relay
editing; bundled desktop Playwright/Chromium.
