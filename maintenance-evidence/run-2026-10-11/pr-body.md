# Sync upstream nanoMuse v1.0.3 (Helm) into the fork (sanitized)

Merges the published upstream release `v1.0.3` into the fork without losing any fork-only
feature, and keeps every `.cn` cloud-backend reference out of the shipped tree.

## Provenance

| | |
|---|---|
| Upstream repository (read-only) | `nano-muse/nanoMuse` |
| Upstream tip merged | `189621240d7efd6a99debc45a4cc1a55edb6b141` (`upstream/main`) |
| Published upstream releases discovered | `v1.0.3` (Helm) — the only release newer than the fork's previous integration point |
| Upstream release commit | `34a950c82977f20006d19d87d2241fe1f7071e7c` (`refs/tags/v1.0.3`) — **an ancestor of `upstream/main`**, 67 commits behind it, so no separate release-commit integration was needed |
| Fork baseline before this run | `f3237f9b697e0fd6c988c1fafcd2bfce830d54fc` (`fork/main`) |
| Previous merge base | `5379e97a5e6d8c68c6f1fc4da3b4649692b94f82` |
| Commits integrated | 180 (`git rev-list --count fork/main..upstream/main`) |
| **Tested head** | `f38a067f851a0b27acdee564ded7e40efb45fab1` (branch `sync/upstream-1.0.3-sanitize`) |
| Diff | 330 files changed, 11,891 insertions(+), 2,298 deletions(−) |

Three commits, each with a DCO `Signed-off-by` line:

```
f38a067f85 test(sync): keep the fork's expectations on two tests upstream 1.0.3 rewrote
df23dbb031 build(web): regenerate committed static from the merged source (Node 22)
c7bd659949 chore(sync): merge sanitized upstream through v1.0.3 (Helm)
```

Releases are discovered independently of whether `upstream/main` moved. Fork releases
already present (`v1.0.0-fork.1`, `v1.0.1-fork.1`, `v1.0.2-fork.1`, `v0.1.41-fork.1`, …)
were deduplicated by upstream tag; `v1.0.3-fork.1` did not exist.

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

Remainder — **18 files**, every one classified, none a new active reference:

```
cloud/README.md                     the deploy artifact name cloud.nanomuse.cn.caddy (cloud/deploy/** is preserved)
docs/zh/cloud.md                    attribution prose for upstream's public relay
docs/zh/every-device.md             attribution prose for upstream's showcase site
docs/zh/privacy.md                  legal text (in the sanitization test's ALLOWED set)
maintenance-evidence/run-2026-10-05/*   immutable prior-run evidence (5 files)
maintenance-evidence/run-2026-10-10/*   immutable prior-run evidence (5 files)
maintenance-evidence/run-2026-10-11/*   this run's evidence — it quotes the scan command (3 files)
maintenance/RUNBOOK.md              this runbook's own literal scan commands
tests/test_fork_relay_defaults.py   absence assertion
tests/test_fork_upstream_037_sanitization.py   absence assertion
tests/test_nudges_runtime.py        absence assertion
```

(The runbook's "as of the 0.1.41 sync" list is 13 files; the extra five are this run's own
evidence files, which necessarily quote `nanomuse\.cn` — the same reason the
`run-2026-10-05` and `run-2026-10-10` files are in the remainder.)

Active-surface scan of the areas the command does not exclude is **empty**:

```
git grep -nI 'nanomuse\.cn|demo\.nanomuse\.dev|nano-muse\.github\.io' -- \
  nanomuse web/src cloud/nanomuse_cloud harness desktop android/src \
  ':(exclude)nanomuse/server/static/**'                        # no hits
grep -rl 'nanomuse\.cn' nanomuse/server/static/                # empty
```

### Contract held

- `NANOMUSE_CLOUD_BASE_URL` / `cloud.base_url` is still the only relay seam.
- `cloud/nanomuse_cloud/config.py`: `invite_url`, `own_key_docs`, `privacy_url`, `repo_url`
  all default to `""`; `openrouter_url` keeps its documented third-party default.
- Empty relay still raises `relay_unconfigured` before any network I/O
  (`nanomuse/cloud.py:46,108`), and the Android path still calls `requireBaseUrl(context)`
  before building a request (`NanoMuseCloud.kt:1129`).
- Upstream's 1.0.3 rewording turned the Chinese docs' relay mentions into bare hostnames
  (`在 \`cloud.nanomuse.cn\` 上`). The fork's "upstream's public relay" attribution was
  re-applied so the text never reads as this fork's own relay, matching `fork/main`.

### Preserved, not rewritten

`CHANGELOG.md` (byte-identical to `upstream/main`), `docs/releases/**`, `docs/privacy.md`,
`docs/roadmap.md`, `docs/readme/**`, `site/README.md`, `docs/release-notes-template.md`,
`cloud/deploy/nanomuse-hk/**`, `demo/showcase/**`, and unrelated third-party `.cn`
citations (`open.bigmodel.cn`, `api.moonshot.cn`, `api.siliconflow.cn`, `open.feishu.cn`,
`pypi.tuna.tsinghua.edu.cn`, `goproxy.cn`, …).

### Generated assets

`nanomuse/server/static/**` is never merged by hand. Commit 1 takes upstream's tree
unchanged; commit 2 replaces it with the output of the merged source built on Node 22
(`vite.config.ts` writes `outDir: "../nanomuse/server/static"`, `emptyOutDir: true`).

## Fork-only features preserved

| Feature | Where | State |
|---|---|---|
| Google Calendar over OAuth | `nanomuse/calendar/feeds.py` | fork's `_refresh_feeds` / `_refresh_google` split kept **and** upstream's `_error_text` URL redaction taken (private feed links are secrets) |
| `relay_unconfigured` before network I/O | `NanoMuseCloud.kt` | `requireBaseUrl(context)` kept inside upstream's refactored `request()` |
| Configurable relay hosting / signed-out relay editing | `nanomuse/server/*`, `web/src/**` | kept |
| Bundled desktop Playwright/Chromium | `scripts/desktop-app/*`, `harness/desktop` | kept |
| Update check: GitHub only, mirror opt-in | `nanomuse/server/update.py` | `INDEX_URL = os.environ.get("NANOMUSE_UPDATE_INDEX_URL", "")`, no default, no fallback |
| `source: 'github' \| 'mirror' \| 'none'` | `harness/dsh-nanomuse/src/desk.ts` | kept |
| Fork badge (no upstream repo ref in the READMEs) | `README.md`, `docs/readme/**` | kept — see the test note below |

No source file present at `fork/main` is missing from this branch. The only 28 files that
disappear are regenerated `nanomuse/server/static/assets/*` bundles.

## Two upstream tests needed a fork-aware expectation

Both arrive with 1.0.3 and fail against the fork's configuration rather than against the
merged code. They are fixed in commit 3, not papered over:

- `tests/test_readme_contributors.py` asserted the badge is
  `hits.sh/github.com/nano-muse/nanoMuse.svg?`. That URL embeds an upstream repository
  reference, which `tests/test_fork_docs_sanitization.py` forbids; the ten READMEs carry
  the fork's komarev badge. The fork's assertion (already present at `fork/main`) is
  restored.
- `tests/test_endpoints_api.py` is new to the fork and posts
  `settings.cloud.base_url + "/v1"` as a custom endpoint, expecting the *"it is the
  account, not an endpoint"* refusal. With the fork's empty relay default that address is
  the relative `/v1`, refused earlier as malformed. The test now asserts the fork's
  behaviour for an unconfigured relay, then sets a relay on the live `Settings` and keeps
  upstream's coverage of the account guard.

## Checks actually run

| Check | Result |
|---|---|
| `pytest -q -m "not live"` (runtime, py3.12 CI venv) | **954 passed, 5 skipped, 1 deselected, 0 failed** |
| Same command at the `fork/main` baseline (`/tmp/nm_base`, `f3237f9b69`) | **854 passed, 5 skipped, 1 deselected, 0 failed** |
| Fork contract tests (3 files) | 143 passed |
| `cloud/` pytest | 178 passed |
| `demo/showcase/gateway` pytest | 44 passed |
| `ruff check nanomuse tests scripts demo cloud` | All checks passed |
| `ruff format --check nanomuse tests scripts` | 229 files already formatted |
| `mypy` (py3.12 venv, `[tool.mypy] files = ["nanomuse"]`) | Success: no issues found in 140 source files |
| `python -m compileall -q demo cloud nanomuse scripts` | clean |
| `web` `npm run check` (lint + tsc + vitest) | exit 0, 105 vitest tests passed |
| `harness/dsh-nanomuse` build + typecheck + test | 313 tests pass, 0 fail |
| `harness/desktop` typecheck + test | 59 tests pass, 0 fail |
| `node scripts/connectors-json.mjs --check` | clean |
| `node scripts/providers-json.mjs --check` | clean |
| End-to-end smoke proof | see below |

The merge adds **100** passing runtime tests and no new failure.

### End-to-end smoke proof (before any expensive build)

`nanomuse serve` v1.0.3 booted on `127.0.0.1:8791` from the merged tree:

- `/api/state` with the Bearer token → **HTTP 200**, `version: "1.0.3"`
- `/api/state` without a token → **HTTP 401** `invalid or missing token`
- all 7 content-hashed assets referenced by `index.html` → **HTTP 200**, including the
  entry chunk `assets/index-tYqPtwPX.js` produced by the regenerated bundle
- a real browser (`chrome-headless-shell`, Chrome for Testing 153.0.8010.12) navigated
  `http://127.0.0.1:8791/#token=…`: the SPA mounted into `<div id="root">` and rendered the
  onboarding copy (*"nanoMuse · Skip setup · Meet your nanoMuse …"*). The only stderr line
  is the known non-GUI-session `CVDisplayLinkCreateWithCGDisplay failed` noise.

## Not verified here

- Windows and Linux desktop installers, the iOS build, and the Android release APK are CI
  and release-time artifacts, not verified in this PR.
- The adversarial review's findings and their disposition are recorded in
  `maintenance-evidence/run-2026-10-11/completion.md` once it has run.
