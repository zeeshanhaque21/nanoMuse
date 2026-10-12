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
| **Tested content head** | `cc4b552a040c53d78d05e57ef88c75c63fb0827d` (branch `sync/upstream-1.0.3-sanitize`) |
| Diff | 334 files changed, 12,087 insertions(+), 2,301 deletions(−) |

Five commits, each with a DCO `Signed-off-by` line. The first four carry all the content;
the only commits after the tested content head are evidence-only edits under
`maintenance-evidence/run-2026-10-11/`, which touch no code:

```
cc4b552a04 fix(docs): restore the sentence period the mirror-clause removal ate, and guard it
204633f988 style(sync): apply ruff format to the three files an earlier sanitization left unformatted
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

Remainder — **19 files**, every one classified, none a new active reference:

```
cloud/README.md                              1   the deploy artifact name cloud.nanomuse.cn.caddy
docs/zh/cloud.md                             3   attribution prose for upstream's public relay
docs/zh/every-device.md                           and upstream's showcase site
docs/zh/privacy.md                                legal text (in the sanitization test's ALLOWED set)
maintenance/RUNBOOK.md                       1   the runbook's own literal scan commands
tests/test_fork_relay_defaults.py            3   absence assertions
tests/test_fork_upstream_037_sanitization.py
tests/test_nudges_runtime.py
maintenance-evidence/run-2026-10-05/*        5   immutable prior-run evidence
maintenance-evidence/run-2026-10-10/*        5   immutable prior-run evidence
maintenance-evidence/run-2026-10-11/pr-body.md 1 this run's PR body — it quotes the scan command
```

(The runbook's "as of the 0.1.41 sync" list is 13 files; the extra six are prior runs'
evidence files plus this run's own, which necessarily quote `nanomuse\.cn`. This run's
`completion.md` will be a 20th once the run finishes.)

Active-surface scan of the areas the command does not exclude is **empty**:

```
git grep -nI 'nanomuse\.cn\|demo\.nanomuse\.dev\|nano-muse\.github\.io' -- \
  nanomuse web/src cloud/nanomuse_cloud harness desktop android/src \
  ':(exclude)nanomuse/server/static/**'                        # no hits
grep -rl 'nanomuse\.cn' nanomuse/server/static/                # empty
```

### Contract held

- `NANOMUSE_CLOUD_BASE_URL` / `cloud.base_url` is still the only relay seam.
- `cloud/nanomuse_cloud/config.py`: `invite_url`, `own_key_docs`, `privacy_url`, `repo_url`
  all default to `""`; `openrouter_url` keeps its documented third-party default.
- Empty relay still raises `relay_unconfigured` before any network I/O
  (`nanomuse/cloud.py`), and the Android path still calls `requireBaseUrl(context)` before
  building a request (`NanoMuseCloud.kt:1129`).
- Upstream's 1.0.3 rewording turned the Chinese docs' relay mentions into bare hostnames
  (`在 \`cloud.nanomuse.cn\` 上`). The fork's "upstream's public relay" attribution was
  re-applied so the text never reads as this fork's own relay, matching `fork/main`.

### Historical and attribution material

Untouched relative to `upstream/main` — no active reference was removed from them:

- `CHANGELOG.md` — byte-identical to `upstream/main`
- `docs/releases/**` — relative to `fork/main` upstream added only its own
  `docs/releases/v1.0.3.md`; the directory carries no fork edit
- `docs/privacy.md`, `site/README.md` — byte-identical to `upstream/main`

Edited relative to `upstream/main` **only** to rename the repository, drop the hosted-demo
and download-mirror references, and bump the version. Their history and their upstream
attribution are kept, not rewritten:

- `docs/readme/README_*.md` (all ten), `docs/release-notes-template.md`, `docs/roadmap.md`
- `cloud/deploy/nanomuse-hk/deploy.sh`
- `demo/showcase/**` (`gateway/showcase_gateway/{config,logs,webpage}.py`, `mirror/traffic.py`)

Unrelated third-party `.cn` citations are untouched: `open.bigmodel.cn`, `api.moonshot.cn`,
`api.siliconflow.cn`, `open.feishu.cn`, `iat-api.xfyun.cn`, `pypi.tuna.tsinghua.edu.cn`,
`goproxy.cn`, and the rest.

### Generated assets

`nanomuse/server/static/**` is never merged by hand. Commit `c7bd659949` takes upstream's
tree unchanged; commit `df23dbb031` replaces it with the output of the merged source built
on Node 22 (`vite.config.ts` writes `outDir: "../nanomuse/server/static"`,
`emptyOutDir: true`). CI's `web app build` job re-runs `npm run build` and fails if the
committed bundle is stale — it is green.

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

No file present at `fork/main` is missing from this branch except regenerated
`nanomuse/server/static/assets/*` bundles; zero non-static files were dropped.

## Three upstream tests needed a fork-aware expectation

These arrive with 1.0.3 and fail against the fork's configuration rather than against the
merged code. They are fixed, not papered over:

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
- `tests/test_fork_docs_sanitization.py` grows a regression test for the sentence-gluing
  scar described under *Review* below.

## Checks actually run

### Local

| Check | Result |
|---|---|
| `pytest -q -m "not live"` (runtime, py3.12 CI venv) | **954 passed, 5 skipped, 1 deselected, 0 failed** |
| Same command at the `fork/main` baseline (`/tmp/nm_base`, `f3237f9b69`) | **854 passed, 5 skipped, 1 deselected, 0 failed** |
| Fork contract tests (3 files) | 144 passed |
| `cloud/` `ruff check . && ruff format --check . && pytest -q` | clean; 178 passed |
| `demo` `ruff check && ruff format --check`; gateway `pytest -q` | clean; 44 passed |
| `ruff check nanomuse tests scripts` / `ruff format --check nanomuse tests scripts` | clean / 229 formatted |
| `mypy` (py3.12 venv, `[tool.mypy] files = ["nanomuse"]`) | Success: no issues found in 140 source files |
| `python -m compileall -q demo cloud nanomuse scripts` | clean |
| `web` `npm run check` (lint + tsc + vitest) | exit 0, 105 vitest tests passed |
| `harness/dsh-nanomuse` build + typecheck + test | 313 tests pass, 0 fail |
| `harness/desktop` typecheck + test | 59 tests pass, 0 fail |
| `node scripts/connectors-json.mjs --check` / `providers-json.mjs --check` | clean |

The merge adds **100** passing runtime tests and no new failure.

### CI

The first pushed head (`f38a067f85`) had **two red jobs**, both `ruff format --check`
failures the fork's own earlier sanitization had left behind and which the local commands
in `AGENTS.md` do not cover (`demo/` and `cloud/` are checked by their own jobs):

- `gateway tests` — `demo/showcase/mirror/traffic.py`
- `relay · ruff and pytest` — `cloud/nanomuse_cloud/config.py:493`,
  `cloud/tests/test_cloud.py:694` (an indentation scar and two expressions laid out for
  upstream's longer URLs)

`ruff format --check demo cloud` reported **11** unformatted files at `fork/main` and **3**
here — the merge already took upstream's formatted versions of the other eight. Commit
`204633f988` applies the repository's own formatter to the remaining three; both jobs are
now green at the current head, as are `Signed-off-by on every commit`, `web app build`,
`build · test · pack` and `build · test (Windows)`.

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

## Review

A separate fresh-context read-only subagent reviewed the diff, independently re-ran the
backend scan and both pytest suites, re-checked the baseline comparison, audited credential
handling and release provenance, and fact-checked this body. **Verdict: safe to merge, no
blockers.**

Its findings, all corrected before the merge:

1. **A real scar** — the mirror-clause removal swallowed a sentence's `.` and the joining
   `;` in `README.md` and five translated readmes, gluing two sentences together. Fixed in
   `cc4b552a04`, with a regression test. (Review listed four readmes; `README_ru.md` had
   the same scar and is fixed too.)
2. **This body's counts were wrong** — the remainder is 19 files, not 18, and this run's
   evidence directory held one file, not three. Corrected above.
3. **The stated tested head was stale and had two red CI jobs.** Corrected above.
4. **"Preserved, not rewritten" was overstated** — several listed paths *are* edited
   relative to `upstream/main`. The section above now separates what is genuinely
   untouched from what was edited, and says why.
5. **The diff stat and tested head were stale.** Both corrected.

## Not verified here

- Windows and Linux desktop installers, the iOS build, and the Android release APK are CI
  and release-time artifacts, not verified in this PR.
- The committed static bundle was structurally checked (every `index.html` asset reference
  exists on disk, no `.cn` strings, no upstream repo refs) and CI rebuilds it, but it was
  not byte-compared against a fresh build in this session.
- The adversarial reviewer did not reproduce the end-to-end smoke proof itself; it verified
  the surrounding evidence instead.
