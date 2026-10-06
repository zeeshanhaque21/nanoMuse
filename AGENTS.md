# AGENTS.md - daily fork maintenance runbook (nanoMuse fork)

Operating notes for the unattended 06:00 America/Los_Angeles sync/validate/release job.
Everything here was learned the hard way on 2026-10-04; each entry is a trap that
actually cost time, with the fix.

**Fork:** `zeeshanhaque21/nanoMuse` (the only writable repo).
**Upstream:** `nano-muse/nanoMuse` - READ-ONLY. Never push, comment, or mutate it.

---

## 0. Read this first: five traps that silently waste a whole run

1. **`timeout` does not exist on this Mac.** `timeout 180 opencode run ...` fails with
   `command not found`. Use `gtimeout` (coreutils) if installed, or run the command with
   the harness `background` flag and read the output file.
2. **`gh-axi` puts `--repo` AFTER the subcommand**, never before:
   `gh-axi pr list --repo zeeshanhaque21/nanoMuse` is correct;
   `gh-axi --repo ... pr list` is not. Also `gh-axi pr list` has **no `--json`**; it takes
   `--fields`, and the available field names are limited (`body, createdAt, labels,
   mergedAt, milestone, url`). For full PR metadata use
   `gh-axi api repos/OWNER/NAME/pulls/N --jq '{...}'`.
3. **The Jetson is `root@jetson-orin-nano`, not your Mac username.** `ssh jetson-orin-nano`
   as `zeeshanhaque` fails with `Permission denied (publickey,password)`. This looks like
   "the box is unreachable" and is not. See §6.
4. **OrbStack is not running at session start.** `docker` fails with
   `dial unix /Users/.../.orbstack/run/docker.sock: no such file or directory`. Fix:
   `orb start`, wait ~8s, then `docker version`. Do not conclude "no container runtime".
5. **A fresh worktree does NOT contain the Android build environment.** `local.properties`
   (the SDK path), `jniLibs/arm64-v8a/libproot.so`, the proot/rootfs assets, and the gradle
   caches exist only in the primary checkout because they are gitignored. See §7.

---

## 1. Model routing

Required model: **Muse Spark 1.3 Free** - `omniroute/opencode/muse-spark-1.3-contributor-free`.
Confirm it resolves before planning work:

```
opencode models --provider omniroute --all      # exact ids: oc/…, opencode/…, opencode-zen/…
```

Invoke it with `--yolo --auto --model …` on every `opencode run`; never stall on an approval.

**Known failure:** on 2026-10-04 this model returned
`[500]: Internal server error (reset after 1m 36s)` on two consecutive native subagent
spawns, and both spawned attempts reported the route as `opencode-zen/…`. A provider outage
is not a task failure - do not burn the run retrying it.

- Retry the worker at most **twice**, then stop and report the provider as blocked.
- If the session model cannot be switched (no model-switch tool), do the work in-session and
  say plainly in the report that the required model could not be confirmed.
- Never silently substitute a different model and present the result as if it ran on Muse Spark.
- Adversarial review must be a **native in-session subagent**, never an HTTP gateway.

---

## 2. Session start: establish state before touching anything

```
cd /Users/zeeshanhaque/Projects/ai-tools/nanoMuse
gh-axi api user --jq .login                 # must be zeeshanhaque21
git remote -v                               # fork + origin must both be the FORK url
treehouse status                            # pool state
gh-axi pr list --repo zeeshanhaque21/nanoMuse --state open
gh-axi release list --repo zeeshanhaque21/nanoMuse
pgrep -fl "opencode run|release-apk"        # a live prior job?
```

Rules that follow from this:

- **Never edit the primary checkout or reset user work.** It carries untracked
  `.artifacts/`, `.deploy-*/`, `build/app-backups/`, `maintenance-evidence/`.
- If a previous sync/release job is still running, or an open PR already covers the same
  upstream commits, **reuse it** - never run a concurrent job or open a duplicate PR.
- Check for existing fork tags/releases **before** creating new ones (§8).

---

## 3. Fetch with explicit refspecs

There is **no `upstream` remote configured** in this clone - only `fork` and `origin`, both
pointing at the fork. Fetch upstream by URL into a tracking ref:

```
git fetch --no-tags fork      '+refs/heads/main:refs/remotes/fork/main' '+refs/heads/*:refs/remotes/fork/*' --prune
git fetch --no-tags origin    '+refs/heads/main:refs/remotes/origin/main'
git fetch --no-tags https://github.com/nano-muse/nanoMuse.git '+refs/heads/main:refs/remotes/upstream/main'
```

Do not trust `FETCH_HEAD` or stale remote-tracking refs.

**treehouse gotcha:** it resolves `--base` against `origin`, so `--base fork/main` fails with
`base branch "fork/main" does not exist`. Fast-forward the local `main` to the freshly fetched
fork head first, then lease from `main`:

```
git merge-base --is-ancestor main origin/main && git branch -f main origin/main
treehouse get --lease --json --base main -b <branch>
```

Only fast-forward `main` after proving it is an ancestor (`git rev-list --count origin/main..main`
must be `0`), so no user commit is lost.

Returning a lease: `treehouse return <path>` refuses to run with uncommitted changes.
Copy evidence out, `git clean` the worktree, then `treehouse return --force <path>`.

---

## 4. Merge and the `.cn` sanitization contract

Merge upstream into a lease branch and resolve by hand. Expect ~29 conflicts on a
multi-release jump.

**Generated assets are never merged and never hand-edited.** `nanomuse/server/static/**`
is a committed build artifact: take upstream's tree, delete files upstream removed, then
**regenerate from the merged source**:

```
cd web && export PATH=/opt/homebrew/opt/node@22/bin:$PATH   # Node 22 REQUIRED; default node is v26
npm ci && npm run build      # writes ../nanomuse/server/static
grep -rl 'nanomuse\.cn' ../nanomuse/server/static/          # must be empty
```

### The contract

The fork must never contact, link to, or default to `nanomuse.cn` (or any `.cn` backend).
Defaults are **empty**, and the operator configures their own relay:

- `NANOMUSE_CLOUD_BASE_URL` / `cloud.base_url` is the only relay seam. Keep it.
- `cloud/nanomuse_cloud/config.py`: `invite_url`, `own_key_docs`, `privacy_url`,
  `repo_url` all default to `""`. `openrouter_url` keeps its documented default -
  it is a third-party key vendor, not a nanoMuse service.
- Empty relay must raise the clear `relay_unconfigured` error **before any network I/O**.
  Never silently fall back to another service.
- Remove at the **owning configuration layer**. A blind global replace is wrong and will
  corrupt unrelated matches.

### Audit an emptied default for unsafe use

Every time a URL default becomes `""`, check each consumer. This was the source of three
real defects found by adversarial review:

| Consumer | Failure when empty | Fix applied |
|---|---|---|
| iOS `NanoMuseAccountView` guide link | `URL(string: "")!` **crashes** | `if let guideURL = URL(string: guide)` |
| Android `call()` | builds a relative URL → OkHttp `IllegalArgumentException` instead of `relay_unconfigured` | call `requireBaseUrl(context)` first |
| Android `DataControlsScreen` privacy row | opens browser on `""`, reports "Copied" for an empty string | row is inert + dimmed when the URL is blank |

Grep for the pattern before declaring sanitization done:
`grep -rn 'openExternalUrl(context, PRIVACY_URL)' android/` and any `URL(string:` force-unwrap.

### Preserve, do not rewrite

Historical/attribution references stay. Report them, never rewrite history:
`CHANGELOG.md`, `docs/releases/**`, `docs/privacy.md`, `docs/roadmap.md`, `docs/readme/**`,
`site/README.md`, `docs/release-notes-template.md`, `cloud/deploy/nanomuse-hk/**`,
`demo/showcase/{Caddyfile,docker-compose.yml,mirror/*}`, and README release-history entries.

Post-merge scan (this exact command is the evidence of record):

```
git grep -l 'nanomuse\.cn' -- . \
  ':(exclude)CHANGELOG.md' ':(exclude)docs/releases/**' ':(exclude)cloud/deploy/**' \
  ':(exclude)demo/**' ':(exclude)docs/privacy.md' ':(exclude)docs/roadmap.md' \
  ':(exclude)docs/readme/**' ':(exclude)site/README.md' \
  ':(exclude)docs/release-notes-template.md' ':(exclude)nanomuse/server/static/**'
```

Expected remainder: at most `README.md`, `docs/every-device.md`, `docs/launch-checklist.md`
(historical, reworded to attribute the site to upstream) and
`tests/test_fork_relay_defaults.py` (the regression test asserting their absence).
**State the actual output.** Do not paste a command whose output you have not seen.

---

## 5. Validation - what actually passes

Run in this order. Cheap first, and get a real end-to-end result before expensive builds.

```
# Python
python3 -m pytest tests/ -q --ignore=tests/test_bridge.py --ignore=tests/test_computer.py \
  --ignore=tests/test_holds.py --ignore=tests/test_mac_window.py \
  --ignore=tests/test_mcp_bridge.py --ignore=tests/test_model_defaults.py
(cd cloud && python3 -m pytest tests -q)                 # 74 passed
(cd demo/showcase/gateway && python3 -m pytest tests -q) # 40 passed
python3 -m ruff check nanomuse tests scripts demo cloud
python3 -m ruff format --check nanomuse tests scripts
(cd web && npm run check)                                # lint + tsc + vitest
python3 -m compileall -q demo cloud nanomuse scripts
```

### Baseline failures - know these before you start

`tests/` is **not** a package (no `__init__.py`), and a `tests` package exists in
`~/.venv-vllm-metal/…/site-packages`. Those six modules fail to collect on a pristine
checkout. Establish the baseline yourself rather than asserting it:

```
git clone --no-checkout --shared <fork-or-worktree> /tmp/nm_base
cd /tmp/nm_base && git fetch <upstream-url> '+refs/remotes/upstream/main:refs/remotes/upstream/main'
git checkout refs/remotes/fork/main     && python3 -m pytest tests/ -q --ignore=<the six>
git checkout refs/remotes/upstream/main && python3 -m pytest tests/ -q --ignore=<the six>
```

As of `34aebbb9f4`: **10 failures, all pre-existing** - `test_config` ×2,
`test_memory_goals`, `test_server` ×4, `test_attachments`, `test_tools`,
`test_channels_api` (the last is new from upstream and absent on the fork).
`cloud/tests` had 1 pre-existing failure on upstream
(`test_admin_health_is_aggregates_only`).

Anything beyond that is a **regression you introduced.** Fix it, do not label it baseline.

### mypy needs a pinned interpreter

The ambient conda python makes mypy die with
`INTERNAL ERROR: maximum semantic analysis iteration count reached` on numpy stubs.
That is a local toolchain artifact, not a code error. Build a 3.12 venv:

```
uv venv --python 3.12 .venv-ci
VIRTUAL_ENV=$PWD/.venv-ci uv pip install -e . mypy
.venv-ci/bin/python -m mypy        # Success: no issues found in 121 source files
```

### Platform-dependent test traps

- `tests/test_desktop_browser_packaging.py` (a **fork-only** test) must use the same
  executable name the script looks for: `nanomuse.exe` on win32, `nanomuse` elsewhere -
  for **both** the fixture and the return-value assertion. Getting this wrong leaves the
  `windows-latest` job red on the fork's own regression test.
- Only `uv`/`python3 -m compileall` compile Python here.

### Android and iOS DO compile locally (corrected 2026-10-05)

An earlier version of this file claimed Android and iOS were "never compiled locally (no
Gradle/Xcode reachable)". **That was wrong, and trusting it made a run report both builds as
"not verified" when they were in fact available.** Verified on this Mac:

- **Android**: the Gradle project root is `android/src/android/` (NOT `android/`) and it has
  `gradlew`, `gradle/`, and a git-ignored `local.properties` pointing at
  `sdk.dir=/Users/zeeshanhaque/Library/Android/sdk`. Gradle 8.11.1, JDK 17 (Zulu) via
  `export JAVA_HOME=$(/usr/libexec/java_home -v 17)`. Release build:
  `cd android/src/android && ./gradlew :app:assembleRelease --console=plain`
- `scripts/release-apk.sh` drives exactly that path, using `android/keystore.properties` and
  `android/nanomuse-release.jks` (both git-ignored, both present since 2026-10-04).
- **iOS**: Xcode 27.0 (build 27A266a), selected at `/Applications/Xcode.app`. Xcode runs and
  resolves the SwiftPM graph, but `xcodebuild` **fails on two missing prebuilt native inputs**:
  `android/src/ios/Configs/ProviderCustomization.xcconfig` (only a `.example` is tracked; copy
  it, it is safe to leave the value empty) and `android/deps/frameworks/Rclone.xcframework`
  (git-ignored, and **absent from the primary checkout too**). Those come from
  `android/deps/build_ffmpeg.sh`, `build_rclone_ios.sh`, etc. Until they are fetched, the
  honest iOS ceiling is a **Swift syntax/type parse**, not a full app build:
  `xcrun swiftc -parse` over `android/src/ios/NanoMuse/*.swift`. Never report iOS as "no
  toolchain" - report which specific native input is missing.
- The prebuilt native asset `android/src/android/app/src/main/jniLibs/arm64-v8a/libproot.so`
  exists in the primary checkout.

### Android release build: the four git-ignored inputs a lease must be given

`assembleRelease` fails on each missing one in turn, which is easy to misread as a broken
toolchain. Copy all four from the primary checkout before building:

| Path | Why |
|---|---|
| `android/src/android/local.properties` | `sdk.dir`; without it Gradle cannot find the SDK |
| `android/src/android/app/libs/rclone.aar` | git-ignored prebuilt Rclone AAR (~9.5 MB) |
| `android/src/android/app/src/main/jniLibs/arm64-v8a/libproot.so` | git-ignored prebuilt proot |
| `android/keystore.properties` + `android/nanomuse-release.jks` | release signing |

`build.gradle.kts` resolves `storeFile` **relative to `app/`**, so the copied
`keystore.properties` must have its `storeFile` repointed at the lease's own copy of the
`.jks` (path only - never print or copy the password values). Verified working result:
`./gradlew :app:assembleRelease` → BUILD SUCCESSFUL, `app-release.apk`, signed
`CN=nanoMuse fork` (signer SHA-256 `811846ed...`), 0 `nanomuse.cn` in the unpacked APK.

**These toolchains live only in the primary checkout** because `local.properties`, the
proot/rootfs assets and the gradle caches are git-ignored. A fresh treehouse lease does NOT
inherit them: wire them in before building (§5 trap). Never report a build as "not verified"
because a runbook line says so - check the toolchain, then report what actually ran.

---

## 6. Jetson relay deploy

```
orb start                     # REQUIRED first; Docker is not running at session start
ssh root@jetson-orin-nano 'docker ps --format "{{.Names}} | {{.Image}} | {{.Status}}"'
```

Layout: `root@jetson-orin-nano`, aarch64, JetPack R39.2.0, busybox userland (no gcc/git/curl/apt),
Docker is the only build path. Current container: `nanomuse-cloud`, image
`nanomuse-cloud:0.1.31-fork.1`, port `127.0.0.1:8787`, data bind
`/mnt/data/nanoMuse-cloud/data -> /srv/nanomuse-cloud/data`, restart `unless-stopped`,
bridge network. Secrets live in the container env - **never print values**; redact to
`<key>=<redacted>` when inspecting.

**Health endpoint is `/healthz`, not `/api/health`.** Verified live:
`https://jetson-orin-nano.time-mora.ts.net/healthz` → `{"ok":true,"version":"0.14.0",…}`.
`/api/health`, `/health` and `/v1/health` all return 404 - do not read that as "relay down".

Deploy (build arm64 on the Mac, stream to the box; keep the old image for rollback):

```
cd <lease> && docker build --platform linux/arm64 -t nanomuse-cloud:0.1.34-fork.1 -f cloud/Dockerfile cloud
docker save nanomuse-cloud:0.1.34-fork.1 | ssh root@jetson-orin-nano docker load
# recreate the container with the SAME env/mounts/ports as the inspect above
curl -sS -m 12 https://jetson-orin-nano.time-mora.ts.net/healthz   # must print ok:true
```

Roll back to the previous image tag if the health check fails. Never expose the relay
publicly, never touch live credentials or OAuth consent during a deploy.

---

## 7. Mac desktop app

```
python3 scripts/desktop-app/build-runtime.py --check
```

- Install Chromium into the bundle with `PLAYWRIGHT_BROWSERS_PATH=0` **before** building;
  the frozen runtime must **navigate a real page**, not merely import Playwright.
- Preserve framework symlinks (`copytree(..., symlinks=True)`).
- The Electron app lives in **`harness/desktop`**, not `desktop/app`. `desktop/app` is retired
  junk from before 0.1.30 and has no runtime; `package-mac.sh` defaults to `harness/desktop`.
  Build it on Node 22 (`/opt/homebrew/opt/node@22/bin`, default node is v26) and ad-hoc sign.
- Full build chain, in this order (verified 2026-10-06):
  `harness/dsh-nanomuse` (`pnpm install --frozen-lockfile && pnpm build`) ->
  `harness/desktop` (`node scripts/prepare-dsh.mjs`, which stages `dsh/`) ->
  a py3.12 venv with `.[hands,browser] pyinstaller`, Chromium installed with
  `PLAYWRIGHT_BROWSERS_PATH=0` ->
  `python scripts/desktop-app/build-runtime.py --check --target harness/desktop/runtime` ->
  `npm run dist:dir` -> `../../scripts/desktop-app/package-mac.sh arm64`.
- Back up under `build/app-backups/` with `ditto` and **verify the backup exists** - version
  reads back and the binary is present - before replacing anything.
- **A running app is not a blocker: stop it, update it, and start it back up.** Quit through
  the app's own path, never `kill -9`:
  `osascript -e 'tell application id "io.github.nanomuse.desktop" to quit'`.
  Confirm it is idle (`pgrep -f '/Applications/nanoMuse.app/Contents/MacOS/nanomuse-desktop'`)
  before replacing, then `open -a /Applications/nanoMuse.app` afterwards.
- **Leave the separate relay alone.** A `nanomuse serve --port 8787` process may be running
  from an older bundle under `build/app-backups/`. That is the user's local relay, not the
  desktop app. Never stop it as part of a desktop update.
- After install: launch, verify the runtime's `/api/health` (a `bearer token is required`
  body means it is up and auth-gated, which is healthy), then verify a **real browser
  navigation** with the bundled Chromium (`--headless=new --dump-dom` over a `data:` or
  `file://` URL), not merely an import of Playwright.

---

## 8. Releases

- Discover upstream releases every run via read-only `gh-axi release list --repo nano-muse/nanoMuse`.
- Start at **v0.1.30**; do not backfill older. Preserve prerelease status.
- Dedup by upstream tag **and** resolved commit recorded in the fork release body.
- Tag `<upstream-tag>-fork.1` at the **sanitized fork commit**, never the raw upstream commit.
- **Never overwrite an existing tag.** Verify existing provenance before treating one as done.
- `v0.1.30-fork.1` / `v0.1.31-fork.1` already exist as drafts from an earlier run.
- **Never copy upstream binary assets** - they may still contain the `.cn` backend and omit
  every fork feature.

### What actually blocks publishing (all verified 2026-10-04)

```
gh-axi secret list --repo zeeshanhaque21/nanoMuse     # count: 0
```

1. **Zero Actions secrets.** The fork has none, so no signed/notarized macOS or Windows
   desktop build is possible (`MAC_CERT_P`, `MAC_CERT_PASSWORD`, `WINDOWS_CERT_P`, and the
   App Store Connect set are all unavailable).
2. **No Android release keystore.** `android/keystore.properties` does not exist anywhere;
   `find . -name 'keystore*'` returns nothing. `build.gradle.kts` falls back to the debug
   key, and `scripts/release-apk.sh` **refuses the debug key** unless passed
   `--allow-debug-key`. Shipping a debug-signed release APK is not acceptable, so the APK
   cannot be produced.
3. **The APK build environment is not in any worktree** - see trap 5. Even with a keystore,
   a lease cannot build it without wiring `local.properties` and the prebuilt native
   artifacts across from the primary checkout.

Therefore: **publish as a draft with the exact blocker**, never as a release that claims
signed artifacts while carrying none. `gh-axi release create <tag> --draft --verify-tag
--body-file <file>`. A code-sync PR may still merge while a release stays blocked -
report those two outcomes separately.

To actually unblock later, a human must: create the Android release keystore, add the
signing secrets, build from the fork tag, then scan every artifact for `nanomuse.cn`
before uploading and only then flip the draft to published.

---

## 9. PR hygiene

- Fork-only PR, base `main`, explicit `--repo zeeshanhaque21/nanoMuse` on every mutation.
- **DCO is enforced**: every non-merge commit needs `Signed-off-by`. Always
  `git commit -s`. The Commits job also enforces Conventional Commit subjects.
- **Never force-push.** If a pushed commit is missing its sign-off, cherry-pick onto a new
  `-v2` branch with `git commit -s` and close the old PR as superseded. (Done this way on
  2026-10-04; PR #9 closed unmerged, PR #10 merged.)
- Merge only when required local checks and available CI pass, review findings are resolved,
  and the **tested head SHA still equals the PR head SHA**. No admin merge, no protection
  bypass, no ignoring failures. If blocked, leave a clearly labelled blocked PR.
- **Ship-aftercare after every push**: re-read the final PR body, confirm the evidence
  commands match their real output, and correct any claim that turns out to be wrong.
- No empty PRs. No-op cleanly when there is nothing to do.

---

## 10. Adversarial review

Spawn a **separate fresh-context native subagent**, read-only, with the literal MODE RULES
preamble plus exact paths and SHAs. It has caught real defects - duplicate assignments,
unwired guards, dead locale keys, over-indented scars, and **false claims in the PR body**.

Instruct it to: verify the diff not the summary; independently re-run the backend scan;
re-verify the "pre-existing failures" claim against a pristine baseline; confirm credential
handling and release provenance; and explicitly list any PR claim that is false or overstated.
Correct the found claims in the PR body rather than leaving them standing.

---

## 11. Evidence and reporting

Keep evidence in the project, never `/tmp`:

```
maintenance-evidence/run-YYYY-MM-DD/{completion.md,pr-body.md,release-<tag>.md}
```

`completion.md` must state: upstream SHA/tag, sanitized fork SHA, PR URL and merge outcome,
the real backend-scan output, checks actually run, review actually performed, release
URLs/status, per-target deploy outcomes with old/new versions, what was **not** verified,
and every remaining blocker. State no-change runs explicitly.

**Never claim a merge, publication, artifact test, review, or deployment that did not
actually happen.** Copy the evidence out of the lease before `treehouse return --force`.

---

## 12. Pre-flight checklist

```
[ ] gh-axi api user -> zeeshanhaque21 ; both remotes are the fork URL
[ ] no prior sync/release job running ; no duplicate open PR
[ ] fork/main + upstream/main fetched with explicit refspecs
[ ] local main fast-forwarded safely (0 unique commits) ; fresh treehouse lease
[ ] conflicts resolved by hand ; static bundle REGENERATED with Node 22
[ ] no .cn in nanomuse/ web/src/ cloud/nanomuse_cloud/ harness/*/src/ desktop/ android/src/ or the bundle
[ ] emptied defaults audited for empty-string misuse
[ ] tests run ; every failure reproduced on a pristine baseline or fixed
[ ] mypy via .venv-ci (py3.12) ; ruff check + format clean ; web npm run check green
[ ] adversarial review done ; confirmed findings fixed ; body claims corrected
[ ] `git commit -s` everywhere ; NO force-push
[ ] CI green on the exact head SHA that was tested
[ ] releases deduped ; tags at the sanitized commit ; drafts if assets are incomplete
[ ] orb start ; ssh root@jetson-orin-nano ; /healthz (not /api/health)
[ ] Mac app quit through its own path, not kill -9 ; backup verified before replacing ; relaunched and health-checked after ; the port-8787 relay left running
[ ] evidence under maintenance-evidence/run-YYYY-MM-DD/
```