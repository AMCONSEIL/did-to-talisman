# Security and testing scope

This is a public test version, not a security-audited release.

Conversion code makes no network calls. Installation downloads pinned public dependencies. The tool decrypts only the encrypted PEM explicitly selected and confirmed by the user, checks it against the supplied DID, then creates and verifies an encrypted Talisman export. It does not modify the original backup or existing wallet files.

Importing gives Talisman a copy of the identity key. A compromised computer, dependency or wallet can put it at risk. Python and Node cannot guarantee physical memory erasure; an encrypted export remains sensitive and Windows permissions inherit from the chosen private folder.

Use the included public-fixture tests first. An independent real Talisman import and controlled signature remain to be confirmed for this generic version. Supported: Ed25519 did:key and encrypted PKCS8 PEM; no claim of compatibility with every DID or wallet.

For test feedback, use GitHub Issues with app version, platform, steps and error code only. Never attach passwords, PEMs, wallet JSON exports or other private material. Redact personal information from screenshots.
