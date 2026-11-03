"""Attribution verification uses only RFC8032 public example keys."""
import copy
import json
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from did_talisman import b58encode
from verify_attribution import attribution_message, make_proof, verify_proof, REPOSITORY

SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
PUBLIC = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
DID = "did:key:z" + b58encode(b"\xed\x01" + PUBLIC)

class AttributionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.dumps({"schema":"did-to-talisman-source-manifest-v1",
            "repository":REPOSITORY,"version":"0.1.1","author_did":DID,
            "source_commit":"1"*40,"source_tree":"2"*40,"byte_representation":"git-blob",
            "files":{}}, sort_keys=True).encode()
        self.message = attribution_message(self.manifest).encode()
        self.key = Ed25519PrivateKey.from_private_bytes(SEED)

    def proof(self, wrapped=False):
        raw = b"<Bytes>"+self.message+b"</Bytes>" if wrapped else self.message
        return make_proof("0x"+self.key.sign(raw).hex(),self.manifest,expected_did=DID)

    def test_raw_signature(self):
        proof=self.proof()
        self.assertEqual("raw",proof["signature_wrapper"])
        self.assertTrue(verify_proof(proof,self.manifest,expected_did=DID)["signature_valid"])

    def test_wallet_bytes_wrapper(self):
        proof=self.proof(True)
        self.assertEqual("substrate-bytes",proof["signature_wrapper"])
        self.assertTrue(verify_proof(proof,self.manifest,expected_did=DID)["signature_valid"])

    def test_modified_message_refused(self):
        proof=self.proof()
        proof["message_utf8"]+="changed"
        with self.assertRaises(ValueError):verify_proof(proof,self.manifest,expected_did=DID)

    def test_modified_manifest_refused(self):
        manifest=json.loads(self.manifest);manifest["source_commit"]="3"*40
        with self.assertRaises(ValueError):
            verify_proof(self.proof(),json.dumps(manifest).encode(),expected_did=DID)

    def test_other_identity_refused(self):
        with self.assertRaises(ValueError):verify_proof(self.proof(),self.manifest)

    def test_modified_signature_refused(self):
        proof=self.proof();proof["signature_hex"]="0x"+bytes(64).hex()
        with self.assertRaises(InvalidSignature):verify_proof(proof,self.manifest,expected_did=DID)

    def test_other_repository_refused(self):
        manifest=json.loads(self.manifest);manifest["repository"]="https://example.org/other"
        with self.assertRaises(ValueError):attribution_message(json.dumps(manifest).encode())

if __name__=="__main__":
    unittest.main()
