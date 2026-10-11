# nanoMuse v1.0.0-fork.1 — sanitized fork release

Tracking upstream [`v1.0.0`](https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.0) ("Keel").

| | |
|---|---|
| Upstream release | https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.0 |
| Upstream tag commit | `a4b3a7aecbab83727ee1961aa726561f9cb08528` |
| **Sanitized fork commit** | the sanitized commit this run produced on `fork/main`; its exact SHA is in `completion.md` |
| Fork tag | `v1.0.0-fork.1` (annotated) on the sanitized commit — **never** the raw upstream commit |
| Merged fork PR | [#17](https://github.com/zeeshanhaque21/nanoMuse/pull/17) |
| Also tracks | `v1.0.2` (Trim), `v1.0.1` (Ballast) — the same sanitized commit |

## Assets

| File | Size | SHA-256 |
|---|---|---|
| `nanoMuse-1.0.2-arm64.apk` | 38,852,775 bytes | `43c3832ed99b7e3cae38cbcc771f5d43197a4c8dd5593100a3d056a1dbb0499e` |
| `nanoMuse-1.0.2-arm64.apk.sha256` | — | the checksum above |

The APK is the one built from the sanitized commit (source `versionName` is upstream's
`1.0.2`; the fork release tag is `v1.0.0-fork.1`). Signature `CN=nanoMuse fork, OU=release,
O=nanoMuse fork`, signer SHA-256 `811846ed…` — the same key as every prior fork release.
**Upstream binary assets are never copied.**

## Sanitization

Same as `v1.0.2-fork.1`: the canonical scan leaves 13 classified files, and the only others are
this run's own four evidence files, which necessarily quote the scan command. The active
surfaces carry no `nanomuse.cn`; the relay seam is `cloud.base_url` / `NANOMUSE_CLOUD_BASE_URL`
only, with no default relay and a `relay_unconfigured` error before any network I/O.

## Fork-only changes kept

Google Calendar; vault-backed MCP headers; configurable relay hosting; signed-out relay
editing; bundled desktop Playwright/Chromium.
