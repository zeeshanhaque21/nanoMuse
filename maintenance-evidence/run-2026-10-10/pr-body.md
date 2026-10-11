# Sync upstream nanoMuse v1.0.0–v1.0.2 into the fork (sanitized)

Merges three published upstream releases into the fork without losing any fork-only
feature, and keeps every `.cn` cloud-backend reference out of the shipped tree.

## Provenance

| | |
|---|---|
| Upstream repository (read-only) | `nano-muse/nanoMuse` |
| Upstream tip merged | `5379e97a5e6d8c68c6f1fc4da3b4649692b94f82` (`upstream/main`) |
| Published upstream releases discovered | `v1.0.0` (Keel) · `v1.0.1` (Ballast) · `v1.0.2` (Trim, Latest) |
| Fork baseline before this run | `df0b3e35986496aa27d48388d5cc24b205252e6e` (`fork/main`) |
| **Sanitized fork commit (this branch head)** | **`244f132c62`** |
| Diff | 405 files changed, 13,266 insertions(+), 2,769 deletions(−) |

Releases are discovered independently of whether `upstream/main` moved; the previous
integration point was the fork's `v0.1.41-fork.1`.

## Sanitization — the scan of record

Post-merge, the canonical scan (this exact command is the evidence of record in
`maintenance/RUNBOOK.md`):

```
git grep -l 'nanomuse\.cn' -- . \
  ':(exclude)CHANGELOG.md' ':(exclude)docs/releases/**' ':(exclude)cloud/deploy/**' \
  ':(exclude)demo/**' ':(exclude)docs/privacy.md' ':(exclude)docs/roadmap.md' \
  ':(exclude)docs/readme/**' ':(exclude)site/README.md' \
  ':(exclude)docs/release-notes-template.md' ':(exclude)nanomuse/server/static/**'
```

Remainder — **13 files**, every one classified, none a new active reference:

```
cloud/README.md                     the deploy artifact name cloud.nanomuse.cn.caddy
docs/zh/cloud.md                    attribution prose for upstream's public relay
docs/zh/every-device.md             attribution prose for upstream's showcase site
docs/zh/privacy.md                  legal text (in the test's ALLOWED set)
maintenance-evidence/run-2026-10-05/*   immutable prior-run evidence (5 files)
maintenance/RUNBOOK.md              this runbook's own literal scan commands
tests/test_fork_relay_defaults.py   absence assertion
tests/test_fork_upstream_037_sanitization.py   absence assertion
tests/test_nudges_runtime.py        absence assertion
```

Active-surface scan of the areas the command does not exclude is **empty**:

```
grep -rn 'nanomuse\.cn' nanomuse/ web/src/ cloud/nanomuse_cloud/ harness/*/src/ android/src/   # no hits
grep -rl 'nanomuse\.cn' nanomuse/server/static/                                                # empty
```

### Contract held

- The relay seam is `cloud.base_url` / `NANOMUSE_CLOUD_BASE_URL` only; no default relay
  is baked in. An empty relay raises `relay_unconfigured` before any network I/O
  (`nanomuse/cloud.py`).
- `cloud/nanomuse_cloud/config.py`: `invite_url`, `own_key_docs`, `privacy_url`,
  `repo_url` all default to `""` (`openrouter_url` keeps its documented third-party default).
- Sanitized at the owning layer, never by a blind global replace.
- The user's private relay (`jetson-orin-nano.time-mora.ts.net`) is not hardcoded and is
  untouched; it is set through the seam.
- Attribution prose and immutable history are preserved, not rewritten.

## Fork-only features preserved (wired, not merely present)

- **Google Calendar** — `nanomuse/tools/calendar_tool.py` and its callers intact.
- **Vault-backed MCP headers** — `nanomuse/server/connections.py` keeps
  `MCPManager([cfg], resolve=lambda v: self.vault.resolve(v, strict=False), redact=self.vault.redact)`.
- **Configurable relay hosting** — the `cloud.base_url` seam, plus the relay in `cloud/`.
- **Signed-out relay editing** — the desktop plugin's relay/cloud client paths intact.
- **Bundled desktop Playwright/Chromium** — `scripts/desktop-app/build-runtime.py` still
  bundles `playwright/.../.local-browsers` into the frozen runtime.

## Generated assets

`nanomuse/server/static/**` was **regenerated from the merged source** with Node 22
(`web && npm run build`), never hand-merged; `grep -rl 'nanomuse\.cn' nanomuse/server/static/`
is empty.

## Checks actually run

| Check | Result |
|---|---|
| `pytest -q -m "not live"` (runtime) | 853 passed, 4 skipped, **2 failed** — both pre-existing on `fork/main` (see below) |
| `ruff check nanomuse tests scripts demo cloud` | All checks passed |
| `ruff format --check nanomuse tests scripts` | 226 files already formatted |
| `mypy` | Success: no issues found in 139 source files |
| `python3 -m compileall -q demo cloud nanomuse scripts` | clean |
| `cloud/` pytest | 170 passed |
| `demo/showcase/gateway` pytest | 44 passed |
| `web` `npm run check` | 100 vitest passed |
| `harness/dsh-nanomuse` build + typecheck + test | 289 tests pass |
| `harness/desktop` typecheck + test | 59 tests pass |
| `node scripts/connectors-json.mjs --check` | clean |
| `node scripts/providers-json.mjs --check` | clean |
| End-to-end smoke proof | `nanomuse serve` booted; SPA mounted; in-browser `/api/state` → 200 `1.0.2`; frozen bundled Chromium (`.local-browsers/chromium-1243`) navigated the real page |
| Android release APK | built from this commit, release-signed, checksum recorded |

### The two failures are pre-existing, not regressions

`tests/test_mac_window.py::test_the_module_imports_without_pyobjc_and_says_so` and
`::test_open_app_sets_the_target_and_computer_target_reports` fail **identically at the
`fork/main` baseline**, run in a pristine worktree (`/tmp/nm_base`, HEAD `df0b3e3598`):

| | passed | failed | skipped |
|---|---|---|---|
| `fork/main` baseline | 807 | **2** | 4 |
| this branch (HEAD `244f132c62`) | 853 | **2** | 4 |

Same two tests, so the merge adds 46 passing tests and no new failures.
`tests/test_mac_window.py`, `nanomuse/computer/**` and `nanomuse/tools/computer.py` are
**byte-identical** between `fork/main` and this branch. The tests assume no window adapter
("Linux, no adapter"), but macOS auto-detects one, so the assertion is host-dependent.

## Releases this run will publish

Fork tags `<upstream>-fork.1` at the sanitized commit (never the raw upstream commit);
upstream binary assets are never copied:

- `v1.0.0-fork.1`, `v1.0.1-fork.1`, `v1.0.2-fork.1`

Assets built from the sanitized commit:

| File | Size | SHA-256 |
|---|---|---|
| `nanoMuse-1.0.2-arm64.apk` | 38,852,775 bytes | `43c3832ed99b7e3cae38cbcc771f5d43197a4c8dd5593100a3d056a1dbb0499e` |

APK verification actually performed: signer `CN=nanoMuse fork, OU=release, O=nanoMuse fork`
(release key, **not** the debug key), signer SHA-256
`811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` — the same key as the
published `v0.1.34-fork.1`, so this build updates an installed copy. Badging:
`io.github.nanomuse.app`, `versionName=1.0.2`, `versionCode=45`, arm64.

## Deployment

Only because this run merges a sanitized sync: redeploy the Jetson relay from `cloud/` and
rebuild/reinstall the Mac desktop app, each backed up and health-checked, with rollback on
failure. The mobile delivery is the signed APK attached to the fork release.
