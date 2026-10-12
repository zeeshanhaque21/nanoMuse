# Run 2026-10-11 — upstream v1.0.3 (Helm) synced into the fork

## Outcome in one line

Upstream `v1.0.3` is merged into `fork/main` through a sanitized PR (#20, merged), the
sanitized relay image is live on the Jetson, and the fork release `v1.0.3-fork.1` is
published with a release-signed, backend-clean Android APK. The Mac desktop app was rebuilt
and installed but **could not be launch-verified from this unattended session** — that is the
one unfinished item, described under *What was not verified*.

## Provenance

| | |
|---|---|
| Upstream repository (read-only) | `nano-muse/nanoMuse` |
| Upstream tip merged | `189621240d7efd6a99debc45a4cc1a55edb6b141` (`upstream/main`) |
| Previous merge base | `5379e97a5e6d8c68c6f1fc4da3b4649692b94f82` |
| Commits integrated | 180 |
| Fork baseline before this run | `f3237f9b697e0fd6c988c1fafcd2bfce830d54fc` (`fork/main`) |
| **Sanitized fork commit** | `51dfee7455f692d4d2044712992038403cde7a74` (`fork/main` after the merge) |
| Tested head (== PR head at merge) | `b1cec00a58d949c404e4f1b9604bbf029b9a506f` |
| Fork PR | [#20](https://github.com/zeeshanhaque21/nanoMuse/pull/20) — **merged**, method `merge`, no admin override, no protection bypass |
| Diff | 334 files changed, 12,087 insertions(+), 2,301 deletions(−) |

Every commit carries a DCO `Signed-off-by`. Nothing was force-pushed; `fork/main` moved only
by the merge.

### Releases discovered

`gh-axi release list --repo nano-muse/nanoMuse` (read-only) found **`v1.0.3` (Helm)** as the
only published release newer than the fork's previous integration point — a stable release,
not a prerelease.

| | |
|---|---|
| Upstream tag object | `ff835524b0ced890dd0738ed48f4d5ef36e19b31` |
| Upstream tag commit (peeled) | `34a950c82977f20006d19d87d2241fe1f7071e7c` — **an ancestor of `upstream/main`** (67 behind), so the release commit was already inside the merge and needed no separate integration |

Fork releases already present (`v1.0.0-fork.1`, `v1.0.1-fork.1`, `v1.0.2-fork.1`,
`v0.1.41-fork.1`, `v0.1.35/36/37-fork.1`, plus the `v0.1.38/39/40-fork.1` provenance drafts)
were deduplicated by upstream tag; `v1.0.3-fork.1` did not exist.

## Backend scan — the real output

Canonical scan (`maintenance/RUNBOOK.md`), run at the final head:

```
git grep -l 'nanomuse\.cn' -- . \
  ':(exclude)CHANGELOG.md' ':(exclude)docs/releases/**' ':(exclude)cloud/deploy/**' \
  ':(exclude)demo/**' ':(exclude)docs/privacy.md' ':(exclude)docs/roadmap.md' \
  ':(exclude)docs/readme/**' ':(exclude)site/README.md' \
  ':(exclude)docs/release-notes-template.md' ':(exclude)nanomuse/server/static/**'
```

**19 files**, every one classified, none a new active reference:

```
cloud/README.md                                  the deploy artifact name cloud.nanomuse.cn.caddy
docs/zh/cloud.md                                 attribution prose for upstream's public relay
docs/zh/every-device.md                          and upstream's showcase site
docs/zh/privacy.md                               legal text (in the sanitization test's ALLOWED set)
maintenance/RUNBOOK.md                           the runbook's own literal scan commands
tests/test_fork_relay_defaults.py                absence assertions
tests/test_fork_upstream_037_sanitization.py     absence assertions
tests/test_nudges_runtime.py                     absence assertion
maintenance-evidence/run-2026-10-05/*            5 immutable prior-run evidence files
maintenance-evidence/run-2026-10-10/*            5 immutable prior-run evidence files
maintenance-evidence/run-2026-10-11/pr-body.md   this run's PR body — it quotes the scan command
```

Active surfaces are **empty**:

```
git grep -nI 'nanomuse\.cn\|demo\.nanomuse\.dev\|nano-muse\.github\.io' -- \
  nanomuse web/src cloud/nanomuse_cloud harness desktop android/src \
  ':(exclude)nanomuse/server/static/**'          # no hits
grep -rl 'nanomuse\.cn' nanomuse/server/static/  # empty
```

The contract held: `NANOMUSE_CLOUD_BASE_URL` / `cloud.base_url` is still the only relay seam;
`invite_url`, `own_key_docs`, `privacy_url`, `repo_url` all default to `""` (with
`github_repo_path` returning `""` rather than a `.cn` fallback); an empty relay still raises
`relay_unconfigured` before any network I/O; Android still calls `requireBaseUrl(context)`.

`nanomuse/server/static/**` was never merged by hand — the merge took upstream's tree, and the
next commit replaced it with a fresh Node 22 `npm run build` output.

## Checks actually run

### Local (at the tested head `b1cec00a58`)

| Check | Result |
|---|---|
| `pytest -q -m "not live"` (py3.12 CI venv) | **955 passed, 5 skipped, 1 deselected, 0 failed** |
| Same, at the `fork/main` baseline `f3237f9b69` | **854 passed, 5 skipped, 1 deselected, 0 failed** |
| Fork contract tests (3 files) | 144 passed |
| `cloud/` ruff check + format + pytest | clean; 178 passed |
| `demo` ruff check + format; gateway pytest | clean; 44 passed |
| root `ruff check` / `ruff format --check` | clean / 229 formatted |
| `mypy` (py3.12 venv) | Success: no issues found in 140 source files |
| `compileall` | clean |
| `web` `npm run check` | exit 0, 105 vitest tests |
| `harness/dsh-nanomuse` build + typecheck + test | 313 pass |
| `harness/desktop` typecheck + test | 59 pass |
| connectors/providers JSON checks | clean |

The merge adds 101 passing runtime tests and no new failure.

### CI at the tested head

All green: `Signed-off-by on every commit`, `web app build`, `gateway tests`,
`relay · ruff and pytest`, `build · test · pack`, `build · test (Windows)`, `docker build`,
`debug APK · arm64-v8a`, `xcodebuild (unsigned)`, `harness bundle`, `Showcase images`,
`Commits`, and the `ubuntu-latest · py3.11/3.12/3.13`, `windows-latest · py3.12`,
`macos-latest · py3.12` matrix. `release` is `skipped` (it is tag-triggered).

Two jobs were red at the **first** pushed head and were fixed, not ignored: `gateway tests`
(`demo/showcase/mirror/traffic.py`) and `relay · ruff and pytest`
(`cloud/nanomuse_cloud/config.py`, `cloud/tests/test_cloud.py`) were unformatted — leftovers
from the fork's earlier sanitization that the runbook's local commands do not cover. Fixed by
running the repository's own formatter on exactly those three files.

### End-to-end smoke proof (before the expensive builds)

`nanomuse serve` v1.0.3 on `127.0.0.1:8791`: `/api/state` with the Bearer token → 200 with
`version: "1.0.3"`; without a token → 401 `invalid or missing token`; all 7 content-hashed
assets referenced by `index.html` → 200, including `assets/index-tYqPtwPX.js`; a real browser
(`chrome-headless-shell`, Chrome for Testing 153.0.8010.12) navigated the live page and the
SPA mounted into `<div id="root">` with the onboarding copy rendered.

## Review actually performed

A separate fresh-context, read-only native subagent reviewed the diff, re-ran the backend scan
and both pytest suites, re-checked the baseline comparison, audited credential handling and
release provenance, and fact-checked the PR body. **Verdict: safe to merge, no blockers**, with
five non-blocking findings — all fixed before the merge:

1. A real scar: the mirror-clause removal swallowed a sentence's `.` and the joining `;` in
   `README.md` and five translated readmes. Fixed in `cc4b552a04` with a regression test.
2. The PR body's remainder count was 18, actually 19; its evidence directory held one file,
   not three.
3. The stated tested head was stale and had two red CI jobs.
4. "Preserved, not rewritten" was overstated — several listed paths *are* edited relative to
   `upstream/main`. The body now separates what is byte-identical from what was edited, and why.
5. The diff stat and tested head were stale.

**Caveat on the review itself:** the subagent's report did not arrive over the messaging
channel; it was recovered by parsing the subagent transcript on disk
(`~/.workbuddy-ai/projects/…/subagents/agent-c29314a29d6844ce.jsonl`) and extracting its
`SendMessage` arguments. The findings above are from that recovered text. A later re-run of
the runtime suite showed the count had moved from 954 to 955 (the new regression test), so the
body's numbers were corrected again in `b1cec00a`.

## Fork release

| | |
|---|---|
| Fork tag | `v1.0.3-fork.1` — annotated, object `cf4ea3ccf2ca5b1a1f5b05b5e233eeb332b046e0`, peeled commit `51dfee7455` (the sanitized fork commit, **never** the raw upstream commit) |
| Release | https://github.com/zeeshanhaque21/nanoMuse/releases/tag/v1.0.3-fork.1 — **published** (`draft: false`, `prerelease: false`, matching upstream's stable status) |
| Assets | `nanoMuse-1.0.3-arm64.apk` (39,054,703 bytes), `nanoMuse-1.0.3-arm64.apk.sha256` |

APK verification actually performed:

| Check | Result |
|---|---|
| Signature | `CN=nanoMuse fork, OU=release, O=nanoMuse fork, L=unset, ST=unset, C=US` — not the debug key |
| Signer SHA-256 | `811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` — the same key as earlier fork releases, so it updates an installed copy |
| Badging | `io.github.nanomuse.app`, `versionName=1.0.3`, `versionCode=46`, arm64-v8a |
| Checksum | `shasum -a 256 -c` → OK; SHA-256 `b686214349a7ee801304881a4d1e5c828badb79e13b77d9af9982aea4df43ded` |
| Backend scan | the APK was fully unzipped and grepped for `nanomuse\.cn`, `demo\.nanomuse\.dev`, `nano-muse\.github\.io`, `cloud\.nanomuse` — **no hits** |

**Build tooling note (not papered over).** `scripts/release-apk.sh` aborted the first time:
it greps apksigner's output for `Signer #1 certificate …`, and build-tools **37.0.0** renamed
those lines to `V2 Signer: certificate …`, so the grep matched nothing and `set -e` killed the
script *after* `assembleRelease` had produced a correctly signed APK. The pipeline was re-run
against a shim `ANDROID_HOME` whose `build-tools/` holds only **36.0.0** (the newest version
that still prints the `Signer #1` form), with the other SDK components symlinked. This is
toolchain drift in the script, not a defect in the merged tree.

## Deployments

### Jetson relay — **done, healthy**

| | |
|---|---|
| Old | `nanomuse-cloud:0.24.2` (carried `nanomuse.cn` defaults for `INVITE_URL`, `OWN_KEY_DOCS`, `PRIVACY_URL`) |
| New | `nanomuse-cloud:0.24.2-fork.1` — built `--platform linux/arm64` from the merged `cloud/`, `docker save \| ssh … docker load` |
| Parity | ports `127.0.0.1:8787→8787`, bind `/mnt/data/nanoMuse-cloud/data:/srv/nanomuse-cloud/data`, `--restart unless-stopped`, bridge network, user `relay`, command `nanomuse-cloud --host 0.0.0.0 --port 8787` |
| Env | recreated from the operator's `/root/nanomuse-cloud.env`; the container's env hash matches the file exactly (`0875e194a6b59a4ee2c2a442a0454492`, 30 lines). **No secret value was printed at any point.** |
| New image scan | `grep nanomuse.cn` inside the image's `nanomuse_cloud/config.py` → **0 hits** |
| Health | `docker ps` → `Up (healthy)`; `https://jetson-orin-nano.time-mora.ts.net/healthz` → `{"ok":true,"version":"0.24.2",…}` (the version is the package version; the fork suffix is an image tag) |
| Rollback | the previous container is kept stopped as `nanomuse-cloud-prev-0.24.2`, the image `nanomuse-cloud:0.24.2` is still on the box, and `/root/nanomuse-cloud.rollback` records `IMAGE=nanomuse-cloud:0.24.2`. **Not needed** |

The relay was not exposed publicly, and no live credentials or OAuth consent were touched.

### Mac desktop app — **installed; launch NOT verified**

Built and verified:

- the frozen runtime (`PyInstaller`, 1,031 MB) with Playwright/Chromium bundled
  (`chromium-1243`, `chromium_headless_shell-1243`, `ffmpeg-1011`), framework symlinks preserved;
  `build-runtime.py --check` started it and got `{'ok': True, 'version': '1.0.3'}`
- the bundled Chromium navigated a real `file://` page and executed its JavaScript
  (`title` became `rendered:2`)
- the `dsh` harness staged into the bundle (374 MB), the Swift **`nanoMuse Computer Use.app`**
  helper built and bundled under `Contents/Helpers` (the runbook's chain omits this step; the
  CI workflow runs it before electron-builder, and without it the app would ship without the
  helper)
- packaged with `package-mac.sh arm64`: helper signed, outer app ad-hoc signed,
  `codesign --verify --strict` → *valid on disk*, *satisfies its Designated Requirement*;
  zip and APK-format dmg written
- **installed** to `/Applications/nanoMuse.app`: `CFBundleShortVersionString` 1.0.3,
  `CFBundleIdentifier io.github.nanomuse.desktop`, signature valid, runtime and helper present

Not verified, and why:

- **The app could not be launched from this session.** Both `open -a` and running the binary
  directly exit immediately (code 0) before the app writes its first log line to
  `~/.nanomuse/desktop/desktop.log`; Electron logs
  `Node.js environment variables are disabled because this process is invoked by other apps`
  and then nothing. A control app (Calculator) launched fine from the same shell, so the
  session can host GUI apps — this is specific to how the automation invokes the bundle. No
  crash report was produced, and there is no quarantine attribute. So `/api/health` and a
  real browser navigation **through the installed app** were not demonstrated.
- **There was nothing to back up or roll back to.** `/Applications/nanoMuse.app` did not exist
  when this run started: its bundle had been deleted before the run while its processes kept
  running as orphans (the log shows the previously installed build was already
  `nanoMuse Desktop 1.0.3`, started 19:43 PT). Those seven orphan processes were stopped with
  **SIGTERM** (never `kill -9`) after `osascript`'s quit could not resolve the deleted bundle.
  The freshly built 1.0.3 app was therefore installed into an empty slot. No `build/app-backups`
  entry was created because there was no current bundle to copy.

### Mobile — **delivered as the release asset**

`nanoMuse-1.0.3-arm64.apk` is attached to `v1.0.3-fork.1` with its checksum; that IS the mobile
delivery. Nothing was installed on a phone. **iOS has no sideload path** in this run — the iOS
sources were not built.

## What was not verified

- The installed Mac app launching, its `/api/health`, and a browser navigation through it (see
  above). This is the run's one real gap.
- Windows and Linux desktop installers, and the iOS build — CI/release-time artifacts, not
  produced here.
- The `.dmg`/`.zip` were written by `package-mac.sh` and the bundle inside was verified, but
  the archives were not mounted and re-verified separately.
- macOS code signing is **ad-hoc only** (`codesign -s -`): the fork has no
  `MAC_CERT_P12_BASE64` / notarization secrets, so Gatekeeper will ask for *Open Anyway*. The
  build is not notarized. No Windows certificate either.

## Remaining blockers

1. **Mac app launch verification** — needs a session that can launch a GUI Electron bundle
   (a normal interactive login), or a documented non-interactive launch path.
2. `scripts/release-apk.sh` and build-tools ≥ 37 — the apksigner output-format change breaks
   the script's signature grep. Worth an upstream-shaped fix (`apksigner verify --print-certs`
   should be parsed for both forms).
3. The runbook's Mac-app chain omits
   `harness/desktop/mac/computer-use/build.sh`, so following it verbatim produces an app
   without the Computer Use helper.

## Housekeeping

- The worktree created for this run is `.worktrees/sync-upstream-1.0.3-sanitize` (a local
  filesystem worktree inside the project — **not** the `~/.cowfs` pool).
- Git-ignored build inputs (`local.properties`, `keystore.properties`, `nanomuse-release.jks`,
  `rclone.aar`, `jniLibs`, the proot assets, `.venv-ci`, `.venv-desktop`, `build/`, `dist/`)
  were staged into the worktree for the builds and never committed.
- No upstream repository was written to at any point; the only writes were to
  `zeeshanhaque21/nanoMuse`.
