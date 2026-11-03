# Implementation references

Checked 2026-11-03; inspect the actual extension before publishing UI instructions.

- did:key and Ed25519 public encoding: https://w3c-ccg.github.io/did-key-spec/
- Encrypted PKCS8 loading and expected key type: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/
- Polkadot keyring: https://polkadot.js.org/docs/keyring/
- Talisman JSON importer, source revision 6d9f18fc2ea8445d1acdd80646c7091c2c8d9c8e:
  https://github.com/TalismanSociety/talisman/blob/6d9f18fc2ea8445d1acdd80646c7091c2c8d9c8e/apps/extension/src/ui/domains/Account/AccountAdd/AccountAddJson/pjsImportPairs.ts
- Public test fixtures, RFC 8032 section 7.1: https://www.rfc-editor.org/rfc/rfc8032#section-7.1

Pinned source compatibility does not substitute for a real independent user test.
