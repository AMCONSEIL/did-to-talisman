# Author and signed version attribution

Author DID: **did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD**

This is a personal community contribution. The author DID is not a default conversion identity; each user provides their own DID.

**Current guided-onboarding version: 0.2.0.** The proof below remains valid for its identified 0.1.1 source commit; it does not cover the later onboarding changes. The same personal author DID is retained.

## Verified attribution / attribution vérifiée

**The attribution signature is verified for version 0.1.1 at source commit [8c35ee3f089c26137f81932ff87893c6bf0d5206](https://github.com/AMCONSEIL/did-to-talisman/commit/8c35ee3f089c26137f81932ff87893c6bf0d5206).**

Repository: https://github.com/AMCONSEIL/did-to-talisman

The holder of the personal DID approved the exact version statement in Talisman. The Ed25519 signature and the signed source manifest were independently checked before publication.

- [Public attribution proof](proofs/v0.1.1-attribution.json)
- [Exact statement](proofs/v0.1.1-statement.txt)
- [Source manifest: 24 files](proofs/v0.1.1-source-manifest.json)
- Manifest SHA256: c609c92aca03495735e698d62151b517dd329a52dabf41b25a78c52f0ed51b37

The signed message begins with the domain separator **DID-TO-TALISMAN-AUTHORSHIP-V1** and binds the author DID, repository, version, complete source commit, Git tree and manifest digest.

Talisman signed using the Substrate bytes wrapper. The exact signed bytes are the UTF-8 bytes of the literal prefix **&lt;Bytes&gt;**, followed by the complete statement, followed by the literal suffix **&lt;/Bytes&gt;**. The proof records this as **substrate-bytes**. It is a message signature, not a funds-transfer transaction.

## Verify locally

After installing the project's dependencies, run in PowerShell:

**.\.venv\Scripts\python.exe verify_attribution.py**

This verifies the exact statement, manifest digest, expected personal DID and Ed25519 signature without accessing a wallet, private key or network.

If the repository was cloned with Git, also verify all source file hashes in the signed commit:

**.\.venv\Scripts\python.exe verify_attribution.py --check-source**

The signed manifest file is preserved byte-for-byte by .gitattributes; its own line endings are part of its signed digest.

The manifest uses **Git blob bytes**. Windows launchers may be exported with CRLF according to .gitattributes; the Git-source check reads the committed blobs rather than a platform-normalized working copy.

## Scope and limits

The proof covers the source commit above and its listed files. The later commit that adds this proof and verifier is not circularly claimed as signed. Future source versions need their own attribution statement.

A valid signature establishes control of the DID key and approval of the attribution statement. It does not independently establish development priority, a security audit, FLOP representation, rewards or a trusted timestamp. The independent Talisman user test described in VALIDATION.md remains separate.

This public proof contains only a message, public identity and signature. It does not contain the wallet backup, private key, seed, password or an API credential.
