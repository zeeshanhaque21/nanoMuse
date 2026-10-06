# Daily NanoMuse fork maintenance — run 2026-10-05

**Outcome: PR #11 opened and CI-green, but NOT merged. No releases created. No deployments performed.**

The merge was blocked by a mandated-gate failure (the separate adversarial review could not
run because the required model provider is down), not by a code defect.

---

## Sync

| | |
|---|---|
| Upstream tip | `10a699280e02827cdae5c81ca1093cda1dea5208` (`upstream/main` = v0.1.37 "Weave") |
| Upstream releases discovered | **v0.1.35** `48fd40d896` (Accord, code 36) · **v0.1.36** `74329deb6e` (Thread, Android/iOS code 37, relay 0.19.0) · **v0.1.37** `10a699280e` (Weave) — all read-only discovery, independent of whether `upstream/main` moved |
| Previous integration | `4f644c9c7ae6a5032b4cfb846a5b0824d1064c72` (upstream v0.1.34), via #10 |
| Base | `9ad7efcedd3895fe49cf1c6a032be835c39d6d3e` (fork `main`) |
| Merge commit | `3e28be36a08808451a53bfbfa64b43a4e13ba724` (true merge, two parents) |
| PR head (final) | `2664e35f0c9d00fec6de8e95b83f3d509700c4ff` |
| PR | **https://github.com/zeeshanhaque21/nanoMuse/pull/11** — open, **not merged** |
| Sanitized fork SHA on `main` | **unchanged** — `9ad7efcedd` (fork `main` was not advanced) |

18 upstream commits across 3 releases were integrated. 54 conflicts resolved.

## Conflict resolution

| Group | Count | Method |
|---|---|---|
| `nanomuse/server/static/**` (generated bundle) | 42 | taken from upstream wholesale, then **regenerated** with the repo's generator (`cd web && npm run build`, Node v22.23.3). Never hand-edited. |
| Real source files | 12 | per-file 3-way merge (`git merge-file --diff3`), each of the 13 conflict hunks resolved explicitly and recorded |

Upstream features preserved and verified **wired**, not merely present: `CloudSettings.sync`;
the console conversation-sync card with its 8 i18n keys in **both** zh and en; the desktop
`SyncControls` rendered at **both** call sites with its 9 locale keys; upstream's new
`docs/cloud.md` sync/one-thread documentation.

## Backend scan (evidence of record)

```
$ git grep -l 'nanomuse\.cn' -- . \
  ':(exclude)CHANGELOG.md' ':(exclude)docs/releases/**' ':(exclude)cloud/deploy/**' \
  ':(exclude)demo/**' ':(exclude)docs/privacy.md' ':(exclude)docs/roadmap.md' \
  ':(exclude)docs/readme/**' ':(exclude)site/README.md' \
  ':(exclude)docs/release-notes-template.md' ':(exclude)nanomuse/server/static/**' \
  ':(exclude)AGENTS.md' ':(exclude)maintenance-evidence/**'
tests/test_fork_relay_defaults.py
tests/test_nudges_runtime.py
```

The remainder is **four** files, not two:

```
README.md
tests/test_fork_relay_defaults.py
tests/test_fork_upstream_037_sanitization.py
tests/test_nudges_runtime.py
```

All three tests assert **absence**. `README.md` is pre-existing release-history prose: it
carries 5 `nanomuse.cn` references, the identical count on `fork/main` before this merge
(verified `git show 9ad7efcedd:README.md | grep -c 'nanomuse\.cn'` -> 5), and none is an
active default. Corrected from an earlier "only the two tests" claim in this report.

### The scan-limited-to-conflicts trap

A scan of conflict-resolved files alone would have reported clean. Upstream reintroduced
the backend in **12 files that did not conflict**, so they auto-merged in silently. Each was
found by classifying every `.cn`-bearing active source file as *new-from-upstream*,
*preserved*, or *removed* against the merge base. Sanitized at the owning layer:

| Surface | Before → After |
|---|---|
| `nanomuse/server/update.py` | `.cn` index always first → fork GitHub first; mirror **opt-in** via `NANOMUSE_UPDATE_INDEX_URL`, empty by default |
| `harness/.../src/desk.ts` | `.cn` index first → `RELEASES_INDEX = ''`, configurable mirror retained |
| `harness/.../src/nudges.ts` | `NUDGES_ORIGIN='https://cloud.nanomuse.cn'` → `''` (feature off until configured) |
| `harness/.../src/client/DevicesPanel.tsx` | `.cn` link → fork releases |
| `web/src/screens/DevicesScreen.tsx` | `.cn` link → fork releases |
| Android `community/UpdateCheck.kt` | `.cn` download + index → fork releases; `INDEX_URL = ""` |
| iOS `NanoMuseUpdateCheck.swift` | `.cn` index → `indexURL = ""` |
| iOS `NanoMuseSettings.swift` | force-unwrapped `.cn` privacy URL → fork's tracked `docs/privacy.md` |
| `harness/.../src/video.ts`, `nanomuse/server/api.py`, `web/src/types.ts`, `web/src/screens/SettingsScreen.tsx`, `docs/{android,app,desktop-muse,every-device,ios,launch-checklist}.md` | doc/comment references describing the old order corrected to match code |

No blind global replacement was used. Emptyed defaults were audited for the three known
unsafe uses, all verified safe: Android `call()` still calls `requireBaseUrl` **before**
building the URL; the Android privacy row is inert+dimmed when blank; the iOS privacy URL is
not force-unwrapped from an empty string.

## Checks actually run on `3e28be36a0` / `c99ccf705e`

| Check | Result |
|---|---|
| Fork relay defaults + new 0.1.37 sanitization tests | **24 passed** |
| `pytest tests/` (runbook's ignores + `test_computer_operator.py`) | **462 passed, 4 skipped, 11 failed** |
| `(cd cloud && pytest tests -q)` | **91 passed** |
| `(cd demo/showcase/gateway && pytest tests -q)` | **40 passed** |
| `ruff check nanomuse tests scripts demo cloud` | **All checks passed** |
| `ruff format --check nanomuse tests scripts` | **203 files already formatted** |
| `mypy` (pinned py3.12 venv) | **Success: no issues found in 128 source files** |
| `cd web && npm run check` | **pass** — tsc clean, **51 vitest tests passed** |
| `cd web && npm run build` (Node 22) | **pass** — regenerated bundle |
| harness `tsc -p tsconfig.json` | **pass** |
| harness `node --test` (after `node build.mjs`) | **132 passed** |
| `python -m compileall` | **pass** |
| In-session invariant assertions | **68 pass, 0 fail** |
| **CI on tested head `c99ccf705e`** | **14 checks, all pass, 0 failures** |

### The 11 failures are pre-existing upstream defects, proven

Verified by cloning pristine checkouts to `/tmp` and running the identical command:

| Checkout | Failures |
|---|---|
| `fork/main` `9ad7efcedd` | **0** |
| `upstream/main` `10a699280e` | **11** |
| this merge `3e28be36a0` | **11** — the *same 11*, identical node ids |

No failure is unique to this merge.

## A real defect this run introduced, and caught

CI failed on the first push: `web app build` → **"Built app is committed"**. Cause: the
committed bundle had been generated **before** the `DevicesScreen.tsx` sanitization landed,
so it was stale. Fixed by regenerating with the repo's generator and committing in
`c99ccf705e`; two consecutive local builds are byte-identical, so the generator is
deterministic. CI re-run: green.

## Review — BLOCKER

**The required separate fresh-context adversarial review could not be run.** The mandated
model `omniroute/opencode/muse-spark-1.3-contributor-free` is unavailable:

| Attempt | Route | Result |
|---|---|---|
| Subagent 1 | `omniroute/opencode/…` | `[500]: Internal server error (reset after 1m 36s)` |
| Subagent 2 | `omniroute/oc/…` | `[500]: Internal server error` |
| Subagent 3 | `omniroute/opencode-zen/…` | `[500]: Internal server error (reset after 1m 36s)` |
| Direct probe | `omniroute/opencode/…` | hung >7 min on "reply OK"; terminated |

Provider outage, not a code problem. Substituting 68 in-session assertions is **not** an
independent review — it is this agent reviewing its own work — so I did **not** merge.

**No admin merge, no protection bypass, no ignored check.**

## Releases — none created

| Item | Status |
|---|---|
| `v0.1.35-fork.1`, `v0.1.36-fork.1`, `v0.1.37-fork.1` | **NOT created.** Tagged releases require a merged sanitized fork commit; the sync did not merge. Creating them now would put fork tags on the wrong commit. |
| Existing `v0.1.30`–`v0.1.34-fork.1` | untouched; verified still on sanitized fork commit `34aebbb9f476`, never a raw upstream SHA |
| No fork tag targets upstream `48fd40d896` / `74329deb6e` / `10a699280e` | verified |
| Android keystore blocker from the prior run | **resolved** — `android/nanomuse-release.jks` + `keystore.properties` now exist, git-ignored; `v0.1.34-fork.1` was published 2026-10-05T01:33Z with a release-signed APK by an earlier run |

## Deployments — none, and correctly so

The runbook permits deployment only when a run **merged** a sync or **published** a release.
Neither happened, so no target was touched. No version changed anywhere.

| Target | Outcome |
|---|---|
| Jetson relay | **not deployed** — versions unchanged. Not contacted. |
| Mac desktop app `/Applications/nanoMuse.app` | **not rebuilt** — versions unchanged. Note: the app **is currently running** (pid 14920 `nanomuse-desktop`), so a future replace would also require it to be idle; I did not kill it. |
| Android APK | **not built** — depends on the unmerged tag |
| iOS | no sideload path on this host |

## Correction (follow-up, 2026-10-05) — my mobile-toolchain claim was WRONG

This report originally stated: *"Android and iOS were never compiled — no reachable
Gradle/Xcode toolchain."* **That was false, and it came from trusting a stale line in
AGENTS.md rather than checking.** Both toolchains exist on this Mac. Verified and corrected:

| Claim | Reality |
|---|---|
| "no reachable Gradle" | **False.** Gradle 8.11.1 + JDK 17 (Zulu) + Android SDK, project root `android/src/android/`. `./gradlew :app:assembleRelease` → **BUILD SUCCESSFUL** |
| "no reachable Xcode" | **False.** Xcode 27.0 (27A266a). `xcodebuild` runs and resolves the SwiftPM graph |

**Android, actually built and scanned** (from merge commit `3e28be36a0`):

| | |
|---|---|
| Artifact | `android/src/android/app/build/outputs/apk/release/app-release.apk`, 33,626,894 bytes |
| SHA-256 | `2b06079e595ee17c6b49c3fd80d5bf4cd79fd5168b5a34cb2505db1f28c5bc36` |
| Signature | `CN=nanoMuse fork, OU=release, O=nanoMuse fork` — a real release key, **not** `CN=Android Debug`; signer SHA-256 `811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` (same key as v0.1.34-fork.1, so it can update an installed copy) |
| Badging | `io.github.nanomuse.app`, versionName 0.1.37, versionCode 38, arm64-v8a |
| `.cn` scan of the **signed** APK | **0 hits** for `nanomuse.cn` across all 592 entries; `classes.dex` 0, `resources.arsc` 0, `AndroidManifest.xml` 0 |
| Old release index | `dl/index.json` **absent entirely** — the mirror index is empty by default, as designed |
| Fork release URL | `https://github.com/zeeshanhaque21/nanoMuse/releases/latest` present in the artifact |
| Remaining `.cn` strings | only third-party BYO-key model providers inside the bundled `libgojni.so` (ModelScope, MiniMax, Moonshot, SiliconFlow, iFlytek, Ark, TBox, SCNet) — not the nanoMuse backend, and not contacted without the user's own key |

The build needed four **git-ignored** inputs that a fresh treehouse lease does not inherit
(`local.properties`, `rclone.aar`, `libproot.so`, the keystore pair). Gradle fails on each in
turn, which is what made this look like a missing toolchain. `build.gradle.kts` resolves
`storeFile` relative to `app/`, so the copied `keystore.properties` needed `storeFile`
repointed at the lease's own copy — path only, no password value was ever printed.

**iOS, honestly bounded.** `xcodebuild` reaches the compile stage and then fails on two
prebuilt native inputs that are git-ignored **and absent from the primary checkout too**:
`Configs/ProviderCustomization.xcconfig` (only a `.example` is tracked) and
`deps/frameworks/Rclone.xcframework`. Those are produced by `android/deps/build_ffmpeg.sh`,
`build_rclone_ios.sh` and friends, which have never been run here. What *did* run:
`xcrun swiftc -parse android/src/ios/NanoMuse/*.swift` → **rc=0, clean**. So the Swift
changes are parse-verified, not app-build-verified. That is the real ceiling today, and it is
a missing prebuilt dependency, **not** a missing toolchain.

AGENTS.md has been corrected in both places so the next run does not repeat this error.

## What was NOT verified

- **No independent adversarial review** (provider outage, above). The largest remaining gap.
- **iOS was not app-built** — blocked on the two unbuilt native dependencies above. Swift
  sources parse clean; that is the limit of what ran.
- **The APK was not built or published during the original run** — it has since been built and
  scanned in the follow-up above, but it is **not attached to any release**, because PR #11 is
  still unmerged and a release artifact must come from a tagged sanitized commit.
- **The Jetson relay, the Mac app, and the phone were not exercised end to end.**
- Whether upstream's 0.1.36/0.1.37 sync feature works against a real relay — only wiring
  and unit-level coverage were verified.

## Remaining blockers

1. **Provider outage** for `muse-spark-1.3-contributor-free` — blocks the mandated review,
   therefore the merge. Retry PR #11 once the provider recovers; CI is already green on
   `2664e35f0c` / `c99ccf705e`.
2. **PR #11 must be merged** before `v0.1.35/36/37-fork.1` can be tagged and released.
3. The Mac desktop app must be **closed by the user** before any future replacement.

## Notes for the next run

- `treehouse` slot 2 was re-leased as `sync/upstream-0.1.37-sanitize` and is **returned by
  this run**. Slot 1 (`docs/daily-runbook`, branch already merged as PR #11 in the prior run)
  is a **pre-existing leftover from an earlier run and was deliberately NOT returned** — this
  run does not own it.
- The primary checkout was never edited: only `git branch -f main origin/main` (a fast-forward
  after proving 0 unique local commits) and untracked `maintenance-evidence/`.
- Lessons worth keeping: (a) a backend scan must classify every `.cn`-bearing file against
  the merge base, not just conflict-resolved ones — auto-merged reintroductions are the norm;
  (b) regenerate the static bundle *after* the last source edit, not before; (c) the
  gh-axi API wrapper returns YAML, and `--jq .body` truncates at code fences — verify PR
  bodies against the rendered page, not the API echo.

## Follow-up commits added to PR #11 during the toolchain correction

| Commit | Purpose |
|---|---|
| `ac1a8ba3b3` | correct the false "never compiled" claim in this report |
| `968b05c108` | correct the stale AGENTS.md line (subject scoped `docs(runbook):` after CI rejected `docs(AGENTS):` - the Commits regex requires a lowercase scope) |

PR #11 head moved past this line as further fixes landed; the authoritative head is the
current `sync/upstream-0.1.37-sanitize` tip, not a SHA quoted in this document.

Two CI failures were hit and fixed honestly rather than bypassed:
1. `web app build` / "Built app is committed" - the committed bundle predated the last source
   edit; regenerated with the repo's generator.
2. `Signed-off-by on every commit` - **not** actually a missing sign-off. Every non-merge
   commit was signed; the real failure was my `docs(AGENTS): ...` subject, because the
   Conventional-Commit regex requires a lowercase scope. The job name is misleading. Fixed by
   amending the subject, and both of CI's own rules were then re-run locally to confirm.

The PR branch was updated with `--force-with-lease` pinned to the exact previously-observed
remote head, never a bare `--force`. No commit was dropped: the only history change is the one
commit message's first line.


---

# FINAL OUTCOME (2026-10-05, after the user's go-ahead)

## Review performed

An **independent fresh-context adversarial review** ran on the model actually available
(Space Bunny Free). Earlier in this run the review was wrongly reported as blocked: the
task file named `omniroute/opencode/muse-spark-1.3-contributor-free`, which returned
`[500]` on three routes and then hung. The available model was the real constraint;
naming a dead route was not a reason to skip the gate. That was my error and it cost a
merge cycle.

The reviewer returned **mergeable after fixes** and found **2 major defects**, both real,
both mine:

1. **Unguarded empty mirror URL.** `UpdateCheck.kt` called `get(INDEX_URL)` with
   `INDEX_URL = ""`. OkHttp's `url("")` throws; it is caught, so no crash, but every
   check made a guaranteed-to-fail request and logged a misleading failure. `update.py`
   and `desk.ts` already guarded - Android and iOS were the only surfaces that did not.
2. **Mobile version lookup still read upstream.** Download went to the fork, the version
   lookup to `nano-muse/nanoMuse`, so the Version row could offer an upstream build.

Both fixed, plus a **third** updater (`com/openminis/app/data/UpdateChecker.kt`) found by
scanning the **built dex** rather than the source - which is exactly what let it hide.
That one predates the merge; it was repointed anyway so the fix is coherent. Four
regression tests added; the mobile scan now walks whole source trees instead of listing
files.

Also corrected from the review: the scan remainder is four files (three absence-asserting
tests + `README.md`'s pre-existing release-history prose), and a stale head SHA.
One reviewer count I re-checked and did **not** adopt: it reported 10 pre-existing
failures against my 11, but its own list contained 11 entries and re-running gives 11.

## Merge

**PR #11 merged** 2026-10-06 as **`ac5877f86d71ce157b408d6c977c1243ff65837d`**
(merge commit, parents preserved - the sanitized merge `3e28be36a0` remains an ancestor).
CI on the tested head: **15 checks, all pass, 0 failures**. No admin merge, no bypass.

Two CI failures were hit and fixed honestly:
- `web app build` / "Built app is committed": the bundle predated the last source edit.
- `Ruff lint` on `UP020` (`io.open`): **CI's ruff is newer than this machine's**, so the
  local run passed while CI failed. Fixed, then re-verified with CI's exact interpreter.

A third cause was the runbook's own stale guidance: it prescribed a pytest ignore-list,
while CI runs `pytest -q -m "not live"` with **no** ignores. The 7 ignored modules fail
to collect locally only because a stray `tests` package in `~/.venv-vllm-metal` shadows
the repo's. Proven pre-existing by running CI's exact command on pristine upstream.

## Releases published

| Tag | Upstream | Sanitized fork commit | Assets |
|---|---|---|---|
| `v0.1.37-fork.1` | v0.1.37 `10a699280e` | `ac5877f86d` | APK + sha256 |
| `v0.1.36-fork.1` | v0.1.36 `74329deb6e` | `ac5877f86d` | APK + sha256 |
| `v0.1.35-fork.1` | v0.1.35 `48fd40d896` | `ac5877f86d` | APK + sha256 |

All three **published** (not drafts), all tagged on the sanitized commit and never on a raw
upstream SHA. All three share one commit because one PR merged all three upstream
releases, so all three carry the same 0.1.37 / versionCode 38 build - stated plainly in
each release body.

**A provenance error I caught and corrected:** the tags were first created on `3e28be36a0`,
the merge *before* the review fixes, which would have shipped a release whose APK contained
code the tag did not. No releases existed yet, so the tags were moved to the real merge
`ac5877f86d` and the APK rebuilt from that exact commit.

## APK (verified end to end, from the tagged commit)

| | |
|---|---|
| Artifact | `nanoMuse-0.1.37-arm64.apk`, 33,626,874 bytes |
| SHA-256 | `93dc51204fac1c1c6406c957ed76f19e8c85d15c657041832673471d11dae41e` |
| Signature | `CN=nanoMuse fork, OU=release` - a real release key, not debug; signer SHA-256 `811846ed...`, the **same key** as v0.1.34-fork.1, so it updates an installed copy |
| Badging | `io.github.nanomuse.app`, 0.1.37, versionCode 38, arm64-v8a |
| `.cn` scan of the **signed** APK | **0** of 592 entries |
| Upstream release refs in dex | **0** (all three updaters read the fork) |

## Deployments

**None.** This run merged a sync and published releases, which permits deployment, but
deployment was not part of this instruction and is a separate, destructive step:
- **Jetson relay** - not contacted, not redeployed.
- **Mac desktop app** - not rebuilt or replaced. It is **currently running**
  (pid 14920), and the rule is to replace only when idle; I did not kill the user's app.
- **Android** - delivered by attaching the verified APK to the releases, which is the
  mobile delivery path. Nothing installed on any phone.
- **iOS** - no sideload path on this host.

## Remaining blockers / not verified

- **macOS and Windows desktop builds not published** - the fork has zero Actions secrets,
  so no signed/notarized artifact is possible here.
- **iOS not app-built** - needs two git-ignored prebuilt native inputs never fetched.
  `swiftc -parse` is clean; that is a parse check, not a device build.
- **Relay and desktop app not exercised** end to end against the new build.
- Conversation sync verified as wired and unit-covered, not against a live relay.
