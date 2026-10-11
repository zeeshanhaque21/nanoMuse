# Daily fork maintenance — run 2026-10-10

**This was not a no-change run.** It merged three published upstream releases into the fork,
sanitized the tree, published three fork releases with a signed Android APK, and redeployed
both delivery targets.

Run started 2026-10-10 (America/Los_Angeles) and finished 2026-10-11 00:35 PDT.

---

## 1. Upstream, fork and the integration point

| | |
|---|---|
| Upstream repository (read-only) | `nano-muse/nanoMuse` |
| Upstream tip merged | `5379e97a5e6d8c68c6f1fc4da3b4649692b94f82` (`upstream/main`) |
| Published upstream releases discovered | `v1.0.0` Keel `a4b3a7aecbab83727ee1961aa726561f9cb08528` · `v1.0.1` Ballast `4f56f9654a6c7f5f7b3f934da4f04f5172e45c42` · `v1.0.2` Trim `7c91811ef16a34fd575c8614fad2ca754088d763` |
| Fork baseline before this run | `df0b3e35986496aa27d48388d5cc24b205252e6e` (`fork/main`) |
| Last fork integration before this run | `v0.1.41-fork.1` |
| Sync branch | `sync/upstream-1.0.2-sanitize-v2` |
| **Head SHA that CI tested** | **`ebec45e248f7d08c58e98b99c215822b0b647b1e`** |
| **Sanitized fork commit (merged)** | **`a73e646d8434fd912d8b1b80badd51f2c4b33c03`** |
| Sanitized tree | `74203ebae26c2ec6a490df2813ab5aa827791374` — **identical** to the tested head's tree, so the merge changed no content |
| Diff vs `fork/main` | 405 files changed, 13,266 insertions(+), 2,769 deletions(−) |

Releases were discovered independently of `upstream/main`: `gh-axi release list --repo nano-muse/nanoMuse`
reports `v1.0.2` (6h before the run) as newest, and no `v1.0.3`.

## 2. PR and merge outcome

| | |
|---|---|
| PR | [#17](https://github.com/zeeshanhaque21/nanoMuse/pull/17) — **MERGED** 2026-10-11T07:26:27Z |
| Merge method | merge commit, no admin override, no protection bypass |
| Superseded | [#16](https://github.com/zeeshanhaque21/nanoMuse/pull/16) closed **unmerged** — its commits `a1973ab78f` and `b33848b957` carried no `Signed-off-by`, which the DCO check rejects |
| Rebuild method | cherry-pick onto `-v2` with `--signoff` per `maintenance/RUNBOOK.md` §9; **no force-push was ever used** |
| Rebuild proof | the superseded head `189ef36e84` and the rebuilt head `e05db9ff5e` both had tree `553837494695326a15474c3ad1693620d12e48e0`; all 9 fork-only non-merge commits carry a `Signed-off-by` |
| Head-SHA discipline | `git rev-parse HEAD` = remote branch head = PR `headRefOid` = `ebec45e248…` at merge time |

### CI on the exact tested head — 17 checks, 16 pass, 0 fail

`SUCCESS`: `build · test · pack` · `build and push` · `docker build` · `gateway tests` ·
`relay · ruff and pytest` · `web app build` · `debug APK · arm64-v8a` · `xcodebuild (unsigned)` ·
`macos-latest · py3.12` · `ubuntu-latest · py3.11` · `ubuntu-latest · py3.12` ·
`ubuntu-latest · py3.13` · `windows-latest · py3.12` · `Signed-off-by on every commit` ·
`what changed` (×2).
`SKIPPED`: `release` — a tag-only workflow, not applicable to a PR.

## 3. The backend scan, as it actually ran

```
git grep -l 'nanomuse\.cn' -- . \
  ':(exclude)CHANGELOG.md' ':(exclude)docs/releases/**' ':(exclude)cloud/deploy/**' \
  ':(exclude)demo/**' ':(exclude)docs/privacy.md' ':(exclude)docs/roadmap.md' \
  ':(exclude)docs/readme/**' ':(exclude)site/README.md' \
  ':(exclude)docs/release-notes-template.md' ':(exclude)nanomuse/server/static/**'
```

**Remainder: 17 files**, every one classified, none a new active reference:

```
cloud/README.md                                    a deploy-artifact filename (cloud.nanomuse.cn.caddy)
docs/zh/cloud.md                                   attribution prose for upstream's public relay
docs/zh/every-device.md                            attribution prose for upstream's showcase site
docs/zh/privacy.md                                 legal text (in the doc test's ALLOWED set)
maintenance-evidence/run-2026-10-05/*  (5 files)   immutable prior-run evidence
maintenance-evidence/run-2026-10-10/*  (4 files)   this run's evidence — it quotes the scan command
maintenance/RUNBOOK.md                             the runbook's own literal scan commands
tests/test_fork_relay_defaults.py                  absence assertion
tests/test_fork_upstream_037_sanitization.py       absence assertion
tests/test_nudges_runtime.py                       absence assertion
```

The runbook's list is 13 files; the four extra are this run's own evidence files, which
necessarily quote `nanomuse\.cn` — the same reason the `run-2026-10-05` files appear.

Active-surface scan of everything the command does **not** exclude is **empty**:

```
grep -rn 'nanomuse\.cn' nanomuse/ web/src/ cloud/nanomuse_cloud/ harness/*/src/ android/src/   # no hits
grep -rl 'nanomuse\.cn' nanomuse/server/static/                                                # empty
grep -rn 'nanomuse\.cn' desktop/                                                               # no hits
```

Contract held: the relay seam is `cloud.base_url` / `NANOMUSE_CLOUD_BASE_URL` only, with no
default relay; an empty relay raises `relay_unconfigured` before any network I/O
(`nanomuse/cloud.py`). In `cloud/nanomuse_cloud/config.py`, `invite_url`, `own_key_docs`,
`privacy_url` and `repo_url` all default to `""` (`openrouter_url` keeps its documented
third-party default). The emptied defaults were audited for empty-string misuse: every
`invite_url` URL build is guarded (`... if self.s.invite_url else ""`), the other three are
metadata passthroughs, and `github_repo_path` handles an empty `repo_url` explicitly
(`re.match` → `None` → `""`). The user's private relay is not hardcoded and was not touched.

## 4. Checks actually run

CI on the tested head is the matrix above. Locally, in the lease:

| Check | Result |
|---|---|
| `pytest -q -m "not live"` (runtime) | 853 passed, 4 skipped, **2 failed** — both pre-existing, see below |
| Fork contract tests (`test_fork_docs_sanitization`, `test_fork_relay_defaults`, `test_fork_upstream_037_sanitization`) re-run in the lease venv | **141 passed** |
| `ruff check nanomuse tests scripts demo cloud` | All checks passed (re-verified this run) |
| `ruff format --check nanomuse tests scripts` | 226 files already formatted (re-verified) |
| `mypy` | Success: no issues found in 139 source files |
| `python3 -m compileall -q demo cloud nanomuse scripts` | clean |
| `cloud/` pytest | 170 passed |
| `demo/showcase/gateway` pytest | 44 passed |
| `web` `npm run check` | 100 vitest passed |
| `harness/dsh-nanomuse` build + typecheck + test | 289 tests pass |
| `harness/desktop` typecheck + test | 59 tests pass |
| `node scripts/connectors-json.mjs --check` | clean (re-verified this run) |
| `node scripts/providers-json.mjs --check` | clean (re-verified this run) |
| `config/config.example.toml` vs code default | `required = false` matches `nanomuse/config.py:584 required: bool = False` (re-verified) |
| End-to-end smoke proof | `nanomuse serve` v1.0.2 booted; in-browser `/api/state` Bearer → 200 `1.0.2`; regenerated content-hashed static assets all 200; frozen bundled Chromium navigated the live page, SPA mounted, no page errors |

### The two failures are pre-existing, not regressions

`tests/test_mac_window.py::test_the_module_imports_without_pyobjc_and_says_so` and
`::test_open_app_sets_the_target_and_computer_target_reports` fail **identically at the
`fork/main` baseline**, run in a pristine worktree (`/tmp/nm_base`, HEAD `df0b3e3598`):

| | passed | failed | skipped |
|---|---|---|---|
| `fork/main` baseline | 807 | **2** | 4 |
| this branch | 853 | **2** | 4 |

Same two tests; the merge adds 46 passing tests and no new failures.
`tests/test_mac_window.py`, `nanomuse/computer/**` and `nanomuse/tools/computer.py` are
byte-identical between `fork/main` and this branch.

## 5. Adversarial review actually performed

A separate fresh-context native subagent ran read-only with the MODE RULES preamble and exact
paths/SHAs. It independently re-ran the scan, re-checked the baseline comparison and inspected
the diff. **Verdict: safe to push/merge, no BLOCKER.** It found 5 documentation defects, all
fixed before the merge, and flagged **2 false claims** in an earlier draft of the PR body
("never by a blind global replace"; "immutable history not rewritten"), which were corrected.
It also caught two blind-replace scars that a global substitution had left:
`.../releases/latestv<version>/` in `docs/release-notes-template.md` and the
`[github.com/…/dl](…/releases/latest)` label/href mismatch in `README.md` and the nine
`docs/readme/*.md`.

## 6. Releases published

Fork tags were created at the **sanitized** commit `a73e646d84`, never at a raw upstream commit.
No upstream binary asset was copied. No existing tag was overwritten.

| Fork tag | Status | Assets |
|---|---|---|
| `v1.0.2-fork.1` | published, **Latest** | `nanoMuse-1.0.2-arm64.apk`, `.sha256` |
| `v1.0.1-fork.1` | published | `nanoMuse-1.0.2-arm64.apk`, `.sha256` |
| `v1.0.0-fork.1` | published | `nanoMuse-1.0.2-arm64.apk`, `.sha256` |

All three tags peel to `a73e646d8434fd912d8b1b80badd51f2c4b33c03` on the remote, and each
release body says so. The `Latest` marker was moved to `v1.0.2-fork.1` because the fork's
READMEs link `releases/latest` — without that, publishing `v1.0.0-fork.1` last had left the
marker there.

### The APK, and what was verified about it

| Check | Result |
|---|---|
| File | `nanoMuse-1.0.2-arm64.apk`, 38,852,775 bytes |
| SHA-256 | `43c3832ed99b7e3cae38cbcc771f5d43197a4c8dd5593100a3d056a1dbb0499e` (matches the recorded `.sha256`) |
| Signature | `CN=nanoMuse fork, OU=release, O=nanoMuse fork` — a real release key, **not** `CN=Android Debug` |
| Signer SHA-256 | `811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` — the same key as `v0.1.34-fork.1`, so it updates an installed copy |
| Badging | `io.github.nanomuse.app`, `versionName=1.0.2`, `versionCode=45`, arm64-v8a |
| Build path | `scripts/release-apk.sh 1.0.2`, with `ANDROID_HOME` pointed at a filtered SDK exposing only build-tools 35.0.0 (what CI pins); build-tools 37.0.0 changes the `apksigner` output format and broke the script's signature grep |

## 7. Deployments

### Jetson relay — **0.22.0-fork.1 → 0.24.1-fork.1** ✅

| | |
|---|---|
| Old | `nanomuse-cloud:0.22.0-fork.1`, container `nanomuse-cloud`, `127.0.0.1:8787`, bind `/mnt/data/nanoMuse-cloud/data → /srv/nanomuse-cloud/data`, restart `unless-stopped`, bridge |
| New | `nanomuse-cloud:0.24.1-fork.1` (built arm64 from this tree's `cloud/`, 291 MB on the box) |
| Method | `docker save \| ssh root@jetson-orin-nano docker load`; the 30 env vars were captured to `/root/nanomuse-cloud.env` (mode 600) and replayed with `--env-file` — **no secret value was ever printed** |
| Rollback kept | container `nanomuse-cloud-pre-0.24.1` (stopped, still present) |
| Health | `https://jetson-orin-nano.time-mora.ts.net/healthz` → `{"ok":true,"version":"0.24.1",…}`; container `Up (healthy)` |

`/healthz` is the endpoint; `/api/health`, `/health` and `/v1/health` 404 and must not be read
as "relay down".

### Mac desktop app — **0.1.41 → 1.0.2** ✅

| | |
|---|---|
| Backup | `build/app-backups/nanoMuse-before-1.0.2-20261011-002945.app` — verified: reads back `0.1.41`, binary present, 1.5 GB |
| Build | `harness/dsh-nanomuse` build → `prepare-dsh.mjs` (22424 files, 374 MB) → py3.12 venv with `.[hands,browser] pyinstaller` + Chromium under `PLAYWRIGHT_BROWSERS_PATH=0` → `build-runtime.py --check` (1048 MB, self-check `{'ok': True, 'version': '1.0.2'}`) → `npm run dist:dir` → `package-mac.sh arm64` |
| Signature | ad-hoc (`codesign --verify --deep --strict` passes). **Not notarized** — the fork has zero Actions secrets, so no Developer ID certificate exists |
| Installed | `/Applications/nanoMuse.app`, `CFBundleShortVersionString` `1.0.2`, staged-then-swapped so the old bundle stayed intact until the new one was verified |
| Launched | `[nanomuse-desktop] nanoMuse Desktop 1.0.2 starting (darwin arm64, packaged=true)`, helper `nanoMuse Computer Use 1.0.2` up, operator `127.0.0.1:55623`, dsh web `127.0.0.1:38421` |
| Health | `curl 127.0.0.1:55500/api/health` → `{"error":"a bearer token is required"}` — up and auth-gated, which is the healthy response |
| Real browser navigation | the installed bundle's own `chrome-headless-shell` (`Google Chrome for Testing 153.0.8010.12`) `--dump-dom` over a `data:` URL returned `<html><head><title>installed-ok</title></head><body><h1 id="t">installed app chromium navigated</h1></body></html>` — a real navigation, not an import of Playwright |
| Old app quit through its own path | `osascript -e 'tell application id "io.github.nanomuse.desktop" to quit'` — no `kill -9` |
| Port-8787 relay | untouched; nothing was listening on 8787 during this run and none was stopped |

**One environment caveat, recorded so it is not mistaken for a defect:** Electron refuses to
start when `NODE_OPTIONS` is set in the environment that launched it
(`Node.js environment variables are disabled because this process is invoked by other apps`).
The agent harness exports `NODE_OPTIONS=--require=…node-language-shim.cjs`, so both
`open -a /Applications/nanoMuse.app` and a direct exec fail **from an agent shell**, while the
same bundle starts normally with `NODE_OPTIONS` unset. `launchctl getenv NODE_OPTIONS` is empty,
so the user's Finder/launchd launch path is unaffected. The app is running now, launched with a
clean environment.

### Mobile delivery

The signed APK is attached to all three fork releases (§6). It was **not** installed on a
physical device in this run.

## 8. What was NOT verified, and remaining blockers

- **No notarized or signed macOS/Windows installer.** The fork has zero Actions secrets, so
  `MAC_CERT_P12_BASE64`, the App Store Connect key set and `WINDOWS_CERT_P12` are all absent.
  The desktop app is ad-hoc signed: it runs locally, but Gatekeeper will ask once on another Mac.
- **The APK was not installed or launched on a device.** Signature, badging and checksum were
  verified; runtime behaviour on Android was not.
- **The relay was health-checked, not exercised end-to-end.** No client turn was driven through
  `https://jetson-orin-nano.time-mora.ts.net` after the redeploy.
- **`xcodebuild` in CI is unsigned** and says nothing about a distributable iOS build.
- **`--headless=new` (the full Google Chrome for Testing binary) hangs** in this non-GUI session
  with `CVDisplayLinkCreateWithCGDisplay failed`. The bundled `chrome-headless-shell` navigates
  correctly, and that is what the browser proof above used. This is an environment limitation of
  the agent session, not of the bundle.
- **The 2 `tests/test_mac_window.py` failures are host-dependent**, not fixed: the tests assume
  no window adapter, but macOS auto-detects one.

No blocker prevented the merge, the releases, or either deployment.

## 9. Cleanup and follow-ups

- The superseded branch `sync/upstream-1.0.2-sanitize` and closed PR #16 remain as a record; the
  superseded head is also on `backup-pre-dco`.
- `/tmp/nm_base` (pristine baseline worktree) and `/tmp/nm-sdk` (filtered Android SDK) are
  scratch and can be removed.
- The lease's `.venv-desktop/` and `harness/desktop/dist/` (zip 658 MB, dmg 764 MB) are build
  outputs; the dmg/zip are **not** published, since without notarization they would be a worse
  first experience than the existing install path.
