# Run 2026-10-06 - rebuild / redeploy all targets

Follow-on to the 2026-10-05 sync run (merge PR #11, releases v0.1.35/36/37-fork.1).
Objective: rebuild and redeploy every deliverable target from the sanitized merged commit.

Sanitized fork commit (all targets built from this): `ac5877f86d71ce157b408d6c977c1243ff65837d`
(merge of PR #11 on fork/main; also the head of `origin/main` as `efe99e6b`).

---

## 1. Jetson relay - REDEPLOYED

| | |
|---|---|
| Old | image `nanomuse-cloud:0.1.34-fork.1`, reporting version `0.14.0` |
| New | image `nanomuse-cloud:0.19.0-fork.1`, reporting version `0.19.0` |

Built arm64 on the Mac from the merged `cloud/` source:

```
docker build --platform linux/arm64 -t nanomuse-cloud:0.19.0-fork.1 -f cloud/Dockerfile cloud
docker save nanomuse-cloud:0.19.0-fork.1 | ssh root@jetson-orin-nano 'docker load'
```

Container recreated with the **same** env, mounts, ports and restart policy as the one it replaced:

- env: captured from the old container into `/root/nanomuse-cloud.env` (mode 600) on the Jetson,
  passed back with `--env-file`; **no secret value was ever printed or copied off the box**
  (31 keys, listed redacted only).
- mounts: `/mnt/data/nanoMuse-cloud/data -> /srv/nanomuse-cloud/data`
- ports: `127.0.0.1:8787 -> 8787/tcp` (loopback only, not public)
- restart: `unless-stopped`; network: `bridge`

Rollback config recorded at `/root/nanomuse-cloud.rollback`; the previous image
`nanomuse-cloud:0.1.34-fork.1` is retained on the box. Rollback was not needed.

Verification (the real client path, over Tailscale):

```
curl -sS -m 15 https://jetson-orin-nano.time-mora.ts.net/healthz
{"ok":true,"version":"0.19.0","models":["gemini/gemini-3.1-flash-lite","wbuddy/deepseek-v4.1-flash"]}
```

`docker ps`: `nanomuse-cloud | nanomuse-cloud:0.19.0-fork.1 | Up (healthy)`.

Note: `curl` does not exist on the Jetson (busybox userland); health was read from inside the
container with `python -c urllib` and from the Mac over Tailscale. `/healthz` is the endpoint;
`/api/health` 404s.

---

## 2. Mac desktop app - REBUILT AND REINSTALLED

| | |
|---|---|
| Old installed | `/Applications/nanoMuse.app` version **0.1.34** (Oct 4) |
| New installed | `/Applications/nanoMuse.app` version **0.1.37** |
| Backup | `build/app-backups/nanoMuse-before-0.1.37-20261006-050849.app` (1.5 GB, version read back 0.1.34, binary present) |

Build chain, all from the merged commit, Node 22 (`/opt/homebrew/opt/node@22/bin`):

1. `harness/dsh-nanomuse`: `pnpm install --frozen-lockfile` + `pnpm build` -> `lib/` (v0.1.37)
2. `harness/desktop`: `node scripts/prepare-dsh.mjs` -> staged `dsh/` (dsh 0.2.0-rc.2,
   dsh-nanomuse 0.1.37, 22,388 files, 373 MB)
3. py3.12 venv `.venv-desktop` with `-e ".[hands,browser]" pyinstaller`; Chromium installed with
   `PLAYWRIGHT_BROWSERS_PATH=0` (chromium-1243, chromium_headless_shell-1243, ffmpeg-1011)
4. `python scripts/desktop-app/build-runtime.py --check --target harness/desktop/runtime`
   -> `runtime: ... (1031 MB)`, `health: {'ok': True, 'version': '0.1.37', 'auth': False}`,
   `the app is served; the bundled runtime works`
5. `npm run dist:dir` -> `dist/mac-arm64/nanomuse-desktop.app`
6. `../../scripts/desktop-app/package-mac.sh arm64` -> ad-hoc signed `nanoMuse.app`,
   `signature ok`, plus `nanoMuse-Desktop-0.1.37-mac-arm64.zip` (654,301,841 bytes) and
   `.dmg` (775,692,677 bytes)

Replace procedure (a running app is **not** a blocker - stop, update, start back up):

- quit through the app's own path:
  `osascript -e 'tell application id "io.github.nanomuse.desktop" to quit'` -> exited in 2 s.
  **Never `kill -9`.**
- confirmed idle, then `rm -rf /Applications/nanoMuse.app` and `ditto` the new bundle in.
- relaunched with `open -a /Applications/nanoMuse.app`.

Post-install verification:

- `CFBundleShortVersionString` = **0.1.37**; `CFBundleIdentifier` = `io.github.nanomuse.desktop`
- `codesign --verify --deep --strict` -> OK
- `Contents/Resources/runtime` and `Contents/Resources/dsh` both present; no quarantine xattr
- process tree came up: main -> dsh -> `runtime/nanomuse mcp` -> renderer
- runtime serving on its port: `/api/health` -> `{"error":"a bearer token is required"}`
  (up and auth-gated = healthy); dsh port -> HTTP 401 (up)
- **real browser navigation** with the bundled Chromium
  (`.../chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/.../Google Chrome for Testing`,
  `--version` = `Google Chrome for Testing 153.0.8010.12`):
  `--headless=new --dump-dom` returned the rendered DOM for both a `data:` URL and a `file://` URL.
  Not merely an import of Playwright.

Current state at time of writing: 0.1.37 installed and running healthy (instance started
08:53:49); no crash reports under `~/Library/Logs/DiagnosticReports/` and no terminate/signal
lines in the unified log.

### Note on `harness/desktop/package-lock.json`

`npm install` in the lease removed two entries from the lockfile's root `dependencies` block:
`@computer-use/mac-screen-capture-permissions` and `@computer-use/node-mac-permissions`. That is
lockfile normalization, not a lost dependency: both are declared in `optionalDependencies` in
`package.json`, and **both are present in the installed 0.1.37 app** at
`Contents/Resources/app.asar.unpacked/node_modules/@computer-use/`, each with a signed
`*.node` (adhoc). The previous 0.1.34 app carried **neither**, so this is an improvement, not a
regression. The lockfile change was reverted in the lease so nothing was committed.

### The separate local relay was left alone

A `nanomuse serve --no-qr --port 8787 --host 127.0.0.1` process (pid 8476) runs from an older
bundle under `build/app-backups/nanoMuse-before-0.1.31-harness.app`. That is the user's local
relay, not the desktop app. It was **not** stopped; it is still listening on 127.0.0.1:8787.

---

## 3. Android APK - already delivered, asset re-verified

The APK was built from the tagged sanitized commit in the 2026-10-05 run and is attached to all
three releases. Re-verified present on `v0.1.37-fork.1`:

- `nanoMuse-0.1.37-arm64.apk`, 33,626,874 bytes, state `uploaded`
- `nanoMuse-0.1.37-arm64.apk.sha256` (checksum `93dc51204fac1c1c6406c957ed76f19e8c85d15c657041832673471d11dae41e`)

No device redeploy: `adb devices` reports an empty device list, so there is no target to install to.

---

## 4. iOS - cannot app-build; parse is the honest ceiling

Both prebuilt native inputs remain absent everywhere (primary checkout included):

- `android/src/ios/Configs/ProviderCustomization.xcconfig` (only the `.example` is tracked)
- `android/deps/frameworks/Rclone.xcframework` (git-ignored)

Therefore no device/simulator build was attempted and none is claimed. The verified ceiling:

```
cd android/src/ios && xcrun swiftc -parse $(find NanoMuse Agent -name '*.swift')
rc=0  errors=0   (163 Swift files)
```

---

## 5. AGENTS.md - corrected and extended

`AGENTS.md` (primary checkout, uncommitted) section 7 was stale and contradicted the update the
user authorized. Both were fixed:

- Electron app path corrected `desktop/app` -> **`harness/desktop`** (desktop/app is retired
  pre-0.1.30 junk with no runtime); documented the full build chain in order.
- Replaced "only replace when the app is idle / report it as blocked" with the standing rule:
  **a running app is not a blocker - stop it, update it, start it back up**, quitting through
  the app's own path and never `kill -9`.
- Added: **leave the separate `nanomuse serve --port 8787` relay alone** during a desktop update.
- Health-check wording now records that `{"error":"a bearer token is required"}` means the
  runtime is up, and that the browser check must be a real navigation, not an import.
- Pre-flight checklist updated to match.

---

## What was NOT verified / remaining blockers

- **iOS app build**: blocked on the two missing prebuilt native inputs above. `swiftc -parse`
  only. Not a toolchain problem - Xcode 27.0 is present.
- **macOS/Windows signed installers**: the fork still has zero Actions secrets
  (`gh-axi secret list` -> count 0), so no Developer ID-signed or notarized artifact is possible.
  The desktop bundle here is **ad-hoc signed only**.
- **Android device install**: no device connected.
- **Jetson secrets**: env values were never printed; only key names were shown redacted.

---

## Evidence

- this file: `maintenance-evidence/run-2026-10-06/completion.md`
- build logs (lease-local, transient): `/tmp/dockerbuild.log`, `/tmp/dsh-install.log`,
  `/tmp/dsh-build.log`, `/tmp/prepare-dsh.log`, `/tmp/runtime-build.log`, `/tmp/desktop-dist.log`,
  `/tmp/package-mac.log`, `/tmp/ios-parse.log`
- artifacts (lease-local): `harness/desktop/dist/mac-arm64/nanoMuse.app`,
  `dist/nanoMuse-Desktop-0.1.37-mac-arm64.{zip,dmg}`
- backup: `build/app-backups/nanoMuse-before-0.1.37-20261006-050849.app`
