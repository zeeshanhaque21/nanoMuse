# nanoMuse v1.0.3-fork.1 — sanitized fork release

Tracking upstream [`v1.0.3`](https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.3) ("Helm").

| | |
|---|---|
| Upstream release | https://github.com/nano-muse/nanoMuse/releases/tag/v1.0.3 |
| Upstream tag object | `ff835524b0ced890dd0738ed48f4d5ef36e19b31` |
| Upstream tag commit (peeled) | `34a950c82977f20006d19d87d2241fe1f7071e7c` — an ancestor of `upstream/main`, so the release needed no separate commit integration |
| **Sanitized fork commit** | `51dfee7455f692d4d2044712992038403cde7a74` (`fork/main`, the merge of PR #20) |
| Fork tag | `v1.0.3-fork.1` — annotated, object `cf4ea3ccf2ca5b1a1f5b05b5e233eeb332b046e0`, peeled commit `51dfee7455`. **Never** the raw upstream commit |
| Merged fork PR | [#20](https://github.com/zeeshanhaque21/nanoMuse/pull/20) |

## Assets

| File | Size | SHA-256 |
|---|---|---|
| `nanoMuse-1.0.3-arm64.apk` | 39,054,703 bytes | `b686214349a7ee801304881a4d1e5c828badb79e13b77d9af9982aea4df43ded` |
| `nanoMuse-1.0.3-arm64.apk.sha256` | — | the checksum above |

Built from the sanitized fork tag on this machine:

```
git checkout v1.0.3-fork.1
ANDROID_HOME=<filtered SDK shim, build-tools 36.0.0> bash scripts/release-apk.sh 1.0.3
```

**Upstream binary assets are never copied** — they may still contain the `.cn` backend and
omit every fork-only change below. Nothing here came from `nano-muse/nanoMuse`'s release.

### Why the build needed an SDK shim

`scripts/release-apk.sh` picks the newest `build-tools` and greps apksigner's output for
`Signer #1 certificate …`. build-tools **37.0.0** renamed those lines to `V2 Signer:
certificate …`, so the grep matches nothing and `set -e` aborts the script *after*
`assembleRelease` has already produced a correctly signed APK. The run therefore ran the
pipeline against a shim `ANDROID_HOME` whose `build-tools/` contains only **36.0.0** (the
newest version that still prints the `Signer #1` form), with `platforms`, `ndk`, `cmake`,
`platform-tools` and `licenses` symlinked to the real SDK. This is a toolchain-drift issue
in the script, not a defect in the merged tree; it is recorded here rather than papered over.

### APK verification actually performed

| Check | Result |
|---|---|
| Signature | `CN=nanoMuse fork, OU=release, O=nanoMuse fork, L=unset, ST=unset, C=US` — a real release key, **not** `CN=Android Debug` |
| Signer SHA-256 | `811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` — the **same key** as `v0.1.34-fork.1` … `v1.0.2-fork.1`, so this build updates an installed copy in place |
| Badging | `package: name='io.github.nanomuse.app' versionCode='46' versionName='1.0.3'`, `application-label:'nanoMuse'`, arm64-v8a |
| Checksum | `shasum -a 256 -c` → `nanoMuse-1.0.3-arm64.apk: OK` |
| Backend scan | the APK was unzipped in full and grepped for `nanomuse\.cn`, `demo\.nanomuse\.dev`, `nano-muse\.github\.io` and `cloud\.nanomuse` — **no hits** |

## Sanitization

The canonical scan (`maintenance/RUNBOOK.md`) leaves **19 files**, every one classified:
attribution prose (`docs/zh/cloud.md`, `docs/zh/every-device.md`), legal text
(`docs/zh/privacy.md`), a deploy-artifact filename (`cloud/README.md`), immutable prior-run
evidence, the runbook itself, this run's own evidence, and three absence-assertion tests. The
active surfaces (`nanomuse/`, `web/src/`, `cloud/nanomuse_cloud/`, `harness/*/src/`,
`desktop/`, `android/src/`, `nanomuse/server/static/`) carry **no** `nanomuse.cn` — the
active-surface grep and the static-bundle grep both return nothing.

The relay seam is `cloud.base_url` / `NANOMUSE_CLOUD_BASE_URL` only; there is no default
relay, and an empty relay raises `relay_unconfigured` before any network I/O.

## Fork-only changes kept

Google Calendar over OAuth; vault-backed MCP headers; configurable relay hosting;
signed-out relay editing; bundled desktop Playwright/Chromium; the GitHub-only update check
with an opt-in mirror; `source: 'github' | 'mirror' | 'none'` in the desktop shell.

## Platform limitations (honest signing status)

- The Android APK is signed with the fork's release key. Verified above.
- The macOS desktop build is **ad-hoc signed** (`codesign -s -`): the fork has no
  `MAC_CERT_P12_BASE64` / notarization secrets, so Gatekeeper will ask for *Open Anyway* in
  System Settings → Privacy & Security. It is not notarized.
- No Windows installer is produced by this run.
- iOS has no sideload path in this run; the iOS sources are only parsed, not built.
