"use strict";
// Sensitive request arrives only on stdin. No outbound network, seed logging or plaintext file.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { Keyring } = require("@polkadot/keyring");
const { cryptoWaitReady, signatureVerify, base58Decode, encodeAddress } = require("@polkadot/util-crypto");

async function main() {
  await cryptoWaitReady();
  if (process.argv.length === 3 && process.argv[2] === "--check") {
    process.stdout.write(JSON.stringify({ready: true, node: process.versions.node}));
    return;
  }
  if (process.argv.length !== 2) throw Error("INVALID_ARGUMENTS");
  let raw = "";
  for await (const chunk of process.stdin) {
    raw += chunk;
    if (raw.length > 32768) throw Error("INPUT_TOO_LARGE");
  }
  const request = JSON.parse(raw);
  raw = "";
  if (typeof request.seed !== "string" || !/^0x[0-9a-f]{64}$/.test(request.seed)) throw Error("INVALID_KEY");
  if (typeof request.password !== "string" || [...request.password].length < 12 ||
      [...request.password].length > 1024) throw Error("INVALID_PASSWORD");
  if (typeof request.did !== "string" || !/^did:key:z[1-9A-HJ-NP-Za-km-z]{46,50}$/.test(request.did))
    throw Error("INVALID_DID");
  const decoded = base58Decode(request.did.slice(9));
  if (decoded.length !== 34 || decoded[0] !== 0xed || decoded[1] !== 1) throw Error("UNSUPPORTED_DID");
  const publicKey = decoded.slice(2);
  const publicHex = "0x" + Buffer.from(publicKey).toString("hex");
  const address = encodeAddress(publicKey, 42);
  if (publicHex !== request.expectedPublicKey || address !== request.expectedAddress) throw Error("IDENTITY_MISMATCH");
  if (typeof request.outputPath !== "string" || !path.isAbsolute(request.outputPath) ||
      path.basename(request.outputPath) !== "account.json") throw Error("INVALID_OUTPUT");
  if (!fs.statSync(path.dirname(request.outputPath)).isDirectory()) throw Error("INVALID_OUTPUT");
  const seed = Buffer.from(request.seed.slice(2), "hex");
  request.seed = "";
  const pair = new Keyring({type: "ed25519", ss58Format: 42}).addFromSeed(seed, {name: "DID - Ed25519"});
  seed.fill(0);
  let restored;
  try {
    if (Buffer.from(pair.publicKey).toString("hex") !== publicHex.slice(2) || pair.address !== address)
      throw Error("KEY_MISMATCH");
    const exported = pair.toJson(request.password);
    const encoding = {content: ["pkcs8", "ed25519"], type: ["scrypt", "xsalsa20-poly1305"], version: "3"};
    if (JSON.stringify(exported.encoding) !== JSON.stringify(encoding)) throw Error("ENCRYPTION_MISMATCH");
    restored = new Keyring({type: "ed25519", ss58Format: 42}).addFromJson(exported);
    restored.decodePkcs8(request.password);
    const message = Buffer.from("DID-TO-TALISMAN-LOCAL-RESTORE-v1|" + request.did + "|" +
                                crypto.randomBytes(16).toString("hex"), "utf8");
    const signature = restored.sign(message);
    if (restored.address !== address || !signatureVerify(message, signature, publicKey).isValid)
      throw Error("RESTORE_CHECK_FAILED");
    const tampered = Buffer.from(message);
    tampered[0] ^= 1;
    if (signatureVerify(tampered, signature, publicKey).isValid) throw Error("NEGATIVE_CHECK_FAILED");
    const serialized = Buffer.from(JSON.stringify(exported, null, 2) + "\n", "utf8");
    // wx refuses every existing target (including symlinks); never overwrite a user's file.
    const fd = fs.openSync(request.outputPath, "wx", 0o600);
    try {
      fs.writeFileSync(fd, serialized);
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
    const written = fs.readFileSync(request.outputPath);
    if (!written.equals(serialized)) throw Error("WRITE_CHECK_FAILED");
    process.stdout.write(JSON.stringify({
      status: "encrypted_export_verified", did: request.did, address, publicKey: publicHex,
      keyType: "ed25519", ss58Format: 42, encoding,
      signatureVerified: true, tamperedMessageRejected: true,
      sha256: crypto.createHash("sha256").update(written).digest("hex"),
    }));
  } finally {
    request.password = "";
    pair.lock();
    if (restored) restored.lock();
  }
}
main().catch(() => {
  // Stable generic code only; no exception, input, password or dependency stack trace.
  process.stderr.write("LOCAL_EXPORT_FAILED");
  process.exitCode = 1;
});
