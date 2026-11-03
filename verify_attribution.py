"""Verify this project's public DID attribution without a wallet or private key."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from did_talisman import identity_from_did, AUTHOR_DID

REPOSITORY = "https://github.com/AMCONSEIL/did-to-talisman"
SCHEMA = "did-to-talisman-attribution-proof-v1"
MANIFEST_NAME = "v0.1.1-source-manifest.json"
PROOF_NAME = "v0.1.1-attribution.json"
DOMAIN = "DID-TO-TALISMAN-AUTHORSHIP-V1\n"

def attribution_message(manifest_bytes):
    manifest = json.loads(manifest_bytes)
    if (manifest.get("schema") != "did-to-talisman-source-manifest-v1"
            or manifest.get("repository") != REPOSITORY
            or manifest.get("version") != "0.1.1"
            or not re.fullmatch(r"[0-9a-f]{40}", manifest.get("source_commit", ""))
            or not re.fullmatch(r"[0-9a-f]{40}", manifest.get("source_tree", ""))
            or manifest.get("byte_representation") != "git-blob"):
        raise ValueError("Unsupported attribution manifest.")
    identity_from_did(manifest["author_did"])
    statement = {
        "purpose": "I attest this project contribution under my personal DID.",
        "project": "did-to-talisman", "version": manifest["version"],
        "repository": manifest["repository"], "author_did": manifest["author_did"],
        "source_commit": manifest["source_commit"], "source_tree": manifest["source_tree"],
        "source_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "scope": "Only the source files listed in this manifest at the identified commit.",
    }
    return DOMAIN + json.dumps(statement, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def verify_proof(proof, manifest_bytes, expected_did=AUTHOR_DID, source_dir=None):
    manifest = json.loads(manifest_bytes)
    message = attribution_message(manifest_bytes)
    if (proof.get("schema") != SCHEMA or proof.get("author_did") != expected_did
            or manifest.get("author_did") != expected_did
            or proof.get("message_utf8") != message
            or proof.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest()):
        raise ValueError("Attribution identity or signed content mismatch.")
    encoded = proof.get("signature_hex", "")
    if not isinstance(encoded, str) or not re.fullmatch(r"0x[0-9a-fA-F]{128}", encoded):
        raise ValueError("An Ed25519 signature of 64 bytes is required.")
    wrapper = proof.get("signature_wrapper")
    if wrapper not in ("raw", "substrate-bytes"):
        raise ValueError("Unsupported signature wrapper.")
    payload = message.encode("utf-8")
    if wrapper == "substrate-bytes":
        payload = b"<Bytes>" + payload + b"</Bytes>"
    public = bytes.fromhex(identity_from_did(expected_did)["public_key"][2:])
    Ed25519PublicKey.from_public_bytes(public).verify(bytes.fromhex(encoded[2:]), payload)
    if source_dir is not None:
        root = Path(source_dir).resolve()
        base = ["git", "--git-dir=" + str(root / ".git"), "--work-tree=" + str(root)]
        commit = manifest["source_commit"]
        tree = subprocess.check_output(base + ["rev-parse", commit + "^{tree}"], text=True).strip()
        if tree != manifest["source_tree"]:
            raise ValueError("Source tree mismatch.")
        for name, entry in manifest["files"].items():
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or name.startswith("-"):
                raise ValueError("Invalid manifest file path.")
            raw = subprocess.check_output(base + ["show", commit + ":" + name])
            if len(raw) != entry["bytes"] or hashlib.sha256(raw).hexdigest() != entry["sha256"]:
                raise ValueError("Source file mismatch: " + name)
    return {"signature_valid": True, "author_did": expected_did,
            "source_commit": manifest["source_commit"], "version": manifest["version"],
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "source_checked": source_dir is not None}

def make_proof(signature_hex, manifest_bytes, expected_did=AUTHOR_DID):
    for wrapper in ("raw", "substrate-bytes"):
        proof = {"schema": SCHEMA, "author_did": expected_did,
                 "signature_algorithm": "Ed25519", "signature_wrapper": wrapper,
                 "message_encoding": "UTF-8", "message_utf8": attribution_message(manifest_bytes),
                 "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                 "signature_hex": signature_hex}
        try:
            verify_proof(proof, manifest_bytes, expected_did)
            return proof
        except Exception:
            pass
    raise ValueError("The signature does not match the expected DID and exact statement.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-source", action="store_true",
                        help="Also verify the signed source commit's Git blob hashes.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = (root / "proofs" / MANIFEST_NAME).read_bytes()
    proof = json.loads((root / "proofs" / PROOF_NAME).read_text(encoding="utf-8"))
    result = verify_proof(proof, manifest, source_dir=root if args.check_source else None)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
