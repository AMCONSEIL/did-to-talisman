# Use your existing DID in Talisman

[Français](TUTORIEL.fr.md) · [Home](README.md)

Author: **Julien / AMCONSEIL**
Author DID: **did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD**

## 1. Prerequisites

Have **your own Ed25519 did:key**, its **existing encrypted PKCS8 PEM backup**, and the backup password. A public DID cannot recover its private key.

If this identity already works in Talisman and can sign, skip conversion. Other source formats need a tested adapter; renaming a file to .pem does not convert it. No replacement identity is generated. Preserve the original backup; importing gives Talisman a copy of the same key.

## 2. Windows setup

1. Install [Python 3.11+](https://www.python.org/downloads/windows/) with Tcl/Tk and its launcher.
2. Install [Node.js 22+](https://nodejs.org/en/download).
3. Extract the complete project, including package-lock.json and requirements.lock.txt.
4. Run **INSTALLER_WINDOWS.cmd** and wait for success.

Setup downloads locked public dependencies from PyPI and npm into the local .venv and node_modules. It reads no backup and requests no DID or password. Its PowerShell execution policy applies only to the setup process; it does not change the system policy.

Technical equivalent: **powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\INSTALLER_WINDOWS.ps1**

After setup, conversion works without an Internet connection.

## 3. Check your public DID

Run **START.cmd** for English, or **LANCER.cmd** for French. Switch languages at any time with **FR / EN** in the window; your inputs are preserved. Enter **your DID**, not the author's DID in this guide, then click **Check DID**.

The tool shows its public key and generic **SS58 42** Substrate address. This step reads no backup and signs nothing. Other DID methods, incomplete identifiers and fragments are refused.

## 4. Create your encrypted export

1. Browse to your own encrypted PEM backup.
2. Enter the backup's **current password**.
3. Choose and confirm a **new export password of at least 12 characters**. This password is for the JSON import, not a password change to the PEM or Talisman.
4. Choose a **private local destination outside the application folder, repositories and public/shared storage**.
5. Confirm the local key-copy consent.
6. Click **Create my encrypted export** and wait for confirmation.

Only this explicit action opens the selected backup. The converter checks the DID/key match, creates an encrypted JSON export, restores it in memory and tests a valid signature and modified-message rejection.

The new folder contains **account.json** and **verification.public.json**. Keep the account file private and its password separately. The report contains public identity data, so sharing it is optional.

A wrong password or identity mismatch stops conversion. An unconfirmed export **must not be imported**. Failure may leave a new result folder; the tool does not remove it. A new attempt creates another folder and never overwrites the source or previous exports.

## 5. Import into Talisman

1. Install the extension from [Talisman's official website](https://www.talisman.xyz/).
2. On first use, configure its local unlock password.
3. Open **+ / Add account → Import → JSON file / Import via JSON**.
4. Select **your account.json** created above.
5. Enter the **new export password**.
6. Select the unlocked account and complete import.

Labels may vary by version. The original personal reference flow used Talisman 3.12.0. An independent user must still follow this new generic package before a stable release.

Do not use **Watch-only**, which can display an account but cannot sign. Never upload the PEM, wallet JSON or passwords to a chat website, GitHub or support.

## 6. Verify identity preservation

Compare the imported account public key with **verification.public.json**. Its address uses generic SS58 format 42. A network prefix can change the displayed address without changing the key. The **public key must match**; stop before transfer or connection if it differs.

The converter's restore check does not substitute for a successful signature from the actual wallet extension.

## 7. Later: connect to FLOP

This kit does not yet include FLOP Chat and makes no FLOP network calls.

When the chat client is available, use current official network settings, connect Talisman, authorize only the matching account, read the official login challenge and sign in the extension. Inspect real quota, expiry and allowed models before prompting.

A login signature is not a transfer. An unexpected transfer is outside this procedure. Native wallet balance and API quota differ; reconnecting does not automatically renew an allowance.

## Troubleshooting

| Problem | Next step |
|---|---|
| Unsupported DID | Use a complete base58btc Ed25519 did:key without a fragment. |
| Source format rejected | Select the real encrypted PKCS8 PEM; renaming is insufficient. |
| Cannot unlock PEM | Check the original backup password, not the export password. |
| Identity mismatch | Find the backup belonging to that DID. |
| Missing dependencies | Run setup again, then reopen the tool. |
| Export not confirmed | Do not import it; preserve the source and inspect the result folder. |
| Different displayed address | Compare public keys and SS58 prefixes without sending funds. |

For a support report, provide only error code and app/Windows/Talisman versions. Never attach passwords or backups; redact personal information from screenshots.
