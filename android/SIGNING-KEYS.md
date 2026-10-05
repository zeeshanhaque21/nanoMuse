# Release signing keys

Offline backups of release signing keys. **This repository is private.**

Each release asset is a keystore for one app. The matching password is in
[`SIGNING-CREDENTIALS.md`](SIGNING-CREDENTIALS.md).

> **⚠️ Key and password are stored together here.** That means anyone with read
> access to this repository can sign builds that phones accept as genuine
> updates, and an Android signing key cannot be rotated for an already-published
> app. See the warning at the top of `SIGNING-CREDENTIALS.md`. The stronger
> arrangement is to keep the password only in a password manager and store just
> the encrypted keystore here.

## Why this exists

An Android release key is the app's permanent identity. Android requires the
**same** key to sign every update, so if a key is lost, no future build can ever
update a copy that is already installed. People would have to uninstall and
re-install, losing app data.

The keystore file on its own is not much of a secret: it is a PKCS12 container
encrypted by its password. Together with the password it is signing capability.
Both are treated as high-sensitivity here.

## Never

- Do not commit a keystore, a `.properties` file, or a password to a **public** repository.
- Do not attach a keystore to a release in a **public** repository. Actions
  artifacts are not private either: on a public repo anyone can download them
  without logging in, and they expire after at most 90 days.
- Do not put a key in an Actions secret, expecting to get it back: secrets are
  write-only, so it could be pushed but never retrieved.
- Do not reuse one key across apps. A key is per-app identity.
- Do not paste a password or keystore into a shell you are echoing, or leave one
  in `/tmp`. Stage it in a variable, write it, then truncate.

## Contents

| Tag | Asset | App | Notes |
|---|---|---|---|
| `nanoMuse-0.1.34` | `nanomuse-release.jks` | nanoMuse (Android) | RSA 4096, self-signed, 30-year validity. Created 2026-10-04. Password in [`SIGNING-CREDENTIALS.md`](SIGNING-CREDENTIALS.md). |

## Restoring a key

1. Download the asset from the matching release below.
2. Verify its SHA-256 against the `.sha256` asset on the same release.
3. Get the password from [`SIGNING-CREDENTIALS.md`](SIGNING-CREDENTIALS.md) or
   the owner's password manager.
4. Place it at `android/nanomuse-release.jks` in the app's checkout, mode `600`.
5. Write `android/keystore.properties` beside it:

       storeFile=nanomuse-release.jks
       storePassword=<from SIGNING-CREDENTIALS.md>
       keyAlias=nanomuse
       keyPassword=<same value>

6. Confirm before relying on it, and check the fingerprint matches the one below:

       keytool -list -v -keystore android/nanomuse-release.jks

Both `*.jks` and `keystore.properties` are git-ignored in the app repositories.

## Verify a build was signed with the expected key

    apksigner verify --print-certs app-release.apk

nanoMuse's key SHA-256 fingerprint is
`811846edf105767ca3e54cdafe5e2cad9e8e3348b1e54aefe6dbee2827512c00`.
A build showing `CN=Android Debug` is **not** a release build.