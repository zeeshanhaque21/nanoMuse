# nanoMuse Android signing key

The release key for nanoMuse lives at `android/nanomuse-release.jks` in this
checkout (mode `600`, git-ignored), with its settings in
`android/keystore.properties` (also git-ignored). Neither file is committed.

## Backup and full instructions

The authoritative copy, the password, the certificate fingerprint, and the
restore procedure are in the **private** repository
[`Leka-AI/signing-keys`](https://github.com/Leka-AI/signing-keys):

| | |
|---|---|
| Keystore | release `nanoMuse-0.1.34`, asset `nanomuse-release.jks` (+ `.sha256`) |
| Password | `SIGNING-CREDENTIALS.md` |
| Alias | `nanomuse` |
| Certificate SHA-256 | `811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00` |
| Fingerprint of the keystore file | `7a473bfecef4cc824e69c4101eeff5c2c55e2588b08619ec470fd0d762b217a0` |

That repo also holds the other apps' keys and the **notes for agents** working on
any of them. Prefer it over this file; this page exists so someone who finds the
key locally knows where the backup is.

## Why losing this key breaks the app

Android requires the **same** signing key for every update of an installed app.
An Android signing key cannot be rotated for an already-published app. If this
key is lost, no future build can update an installed copy: people would have to
uninstall, losing app data.

Back the key up, and keep the password somewhere that is not only this Mac.

## Verify a build is signed with this key

    apksigner verify --print-certs android/src/android/app/build/outputs/apk/release/app-release.apk

Compare the certificate SHA-256 with the value above. `CN=Android Debug` means
the build is **not** a release build. Do not ship it, and do not pass
`--allow-debug-key` to `scripts/release-apk.sh` to work around a missing
keystore.

## Security posture of the backup

2FA is enabled on the owning account (confirmed 2026-10-04). The private repo
has one collaborator, `zeeshanhaque21`, and no deploy keys.

The backup stores the key **and** its password in one place, which is weaker
than splitting them: anyone with read access can sign builds devices accept as
genuine updates, and that cannot be undone. Moving the password to a password
manager and keeping only the encrypted keystore in the repo would close that.

2FA protects login only. A leaked personal access token or OAuth grant bypasses
it entirely, so keep tokens fine-grained and scoped.