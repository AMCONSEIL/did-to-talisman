# Validation — 0.1.1 public test version

## Checked

- Windows, Python 3.11 / Tk 8.6; Node.js 24.13.1; Polkadot 14.0.3; cryptography 48.0.0.
- 17 offline automated tests with two **public RFC 8032 identities**, never the author's key.
- Both identities preserve their public key and address; Python public encoding is cross-checked by Polkadot utilities.
- Encrypted JSON v3 restoration, successful signature, modified-message rejection and source preservation.
- Wrong DID/password/key type, plaintext PEM, unsupported DID, incomplete setup and output collisions refused.
- Existing output preserved; helper errors do not echo input.
- French/English GUI startup, live language switching preserving all inputs, feedback and consent, and small-window scrolling.
- Empty identity/password fields and explicit consent gate.
- Modern responsive cards, visible keyboard focus and in-window FR/EN selection; the conversion core and Node crypto helper are unchanged.
- Windows GUI visually inspected; documentation screenshot has no user identity or files.
- Fresh setup from locked dependencies in another folder containing spaces: passed. All 15 pre-redesign tests also passed in that clean copy.

Run: **.\.venv\Scripts\python.exe -m unittest discover -s tests -v**

## Before a stable release

An independent user must follow setup, use their own supported backup, import the result into Talisman and complete a controlled signature. The original identity-specific procedure worked in Talisman 3.12.0; this does not automatically validate every installation of this generic package.

No universal DID/wallet compatibility, security audit, hardware-key support, FLOP inference success or reward attribution is claimed.

No real key was opened for these checks. The tool/tests do not query a blockchain, request a faucet, enroll a FLOP account or modify infrastructure.

## Reproducibility and local data

Node: exact versions and integrity in package-lock.json, lifecycle scripts disabled. Python: exact versions and published wheel hashes in requirements.lock.txt.

.venv, node_modules, validation.local, archives and wallet/key files are excluded from source delivery. Tests clean up only their own temporary public fixture files. Runtime does not delete or overwrite backups/exports.

Original personal tools are preserved. Rollback for this isolated addition is to stop using its launchers; existing tools continue to work.
