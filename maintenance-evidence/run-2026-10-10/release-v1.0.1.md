# nanoMuse v1.0.1-fork.1 — sanitized fork release

Tracking upstream [`v1.0.1`](https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.1) ("Ballast").

| | |
|---|---|
| Upstream release | https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.1 |
| Upstream tag commit | `4f56f9654a6c7f5f7b3f934da4f04f5172e45c42` |
| **Sanitized fork commit** | the sanitized commit this run produced on `fork/main`; its exact SHA is in `completion.md` |
| Fork tag | `v1.0.1-fork.1` (annotated) on the sanitized commit — **never** the raw upstream commit |
| Also tracks | `v1.0.2` (Trim), `v1.0.0` (Keel) — the same sanitized commit |

## Assets

| File | Size | SHA-256 |
|---|---|---|
| `nanoMuse-1.0.2-arm64.apk` | 38,852,775 bytes | `43c3832ed99b7e3cae38cbcc771f5d43197a4c8dd5593100a3d056a1dbb0499e` |
| `nanoMuse-1.0.2-arm64.apk.sha256` | — | the checksum above |

The APK is the one built from the sanitized commit (source `versionName` is upstream's
`1.0.2`; the fork release tag is `v1.0.1-fork.1`). Signature `CN=nanoMuse fork, OU=release,
O=nanoMuse fork`, signer SHA-256 `811846ed…` — the same key as every prior fork release.
**Upstream binary assets are never copied.**

## Sanitization

Same as `v1.0.2-fork.1`: the canonical scan leaves 13 classified files; the active surfaces
carry no `nanomuse.cn`; the relay seam is `cloud.base_url` / `NANOMUSE_CLOUD_BASE_URL` only,
with no default relay and a `relay_unconfigured` error before any network I/O.

## Fork-only changes kept

Google Calendar; vault-backed MCP headers; configurable relay hosting; signed-out relay
editing; bundled desktop Playwright/Chromium.
