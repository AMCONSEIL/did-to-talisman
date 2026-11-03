"""Only RFC 8032 public test vectors. Never read any user's wallet or configuration."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import did_talisman as app
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# RFC 8032, section 7.1. Public examples, never use these identities for funds.
VECTORS = [
    ("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
     "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"),
    ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
     "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c"),
]
OLD_PASSWORD = "RFC8032-public-fixture-only"
NEW_PASSWORD = "Demo-export-only-2026!"

def fixture_did(index=0):
    return "did:key:z" + app.b58encode(b"\xed\x01" + bytes.fromhex(VECTORS[index][1]))

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="public-did-test-")
        self.path = Path(self.directory.name)
        self.pem = self.path / "public-rfc8032-fixture.pem"
        key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(VECTORS[0][0]))
        self.pem.write_bytes(key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(OLD_PASSWORD.encode())))
        self.original = self.pem.read_bytes()
        self.output = self.path / "output"
        self.output.mkdir()

    def tearDown(self):
        # Only this test's TemporaryDirectory, containing known public fixtures, is cleaned up.
        self.directory.cleanup()

    def run_export(self, index=0, password=NEW_PASSWORD):
        return app.export_existing(fixture_did(index), self.pem, OLD_PASSWORD, password, self.output)

    def assert_error(self, expected, *args):
        with self.assertRaises(app.ExportError) as result:
            app.export_existing(*args)
        self.assertEqual(expected, result.exception.code)
        self.assertEqual(self.original, self.pem.read_bytes())

    def test_public_did_mapping(self):
        for i in range(2):
            identity = app.identity_from_did(fixture_did(i))
            self.assertEqual("0x" + VECTORS[i][1], identity["public_key"])
            self.assertTrue(identity["address"].startswith("5"))
        self.assertNotEqual(app.identity_from_did(fixture_did(0))["address"],
                            app.identity_from_did(fixture_did(1))["address"])

    def test_unsupported_or_malformed_dids(self):
        for did in ("", "did:web:example.org", "did:key:z0", fixture_did()+"#key-1",
                    fixture_did()+"?q=1", " " + fixture_did(), "did:key:z" + "1"*200,
                    "did:key:z"+app.b58encode(b"\xe7\x01"+bytes(33))):
            with self.subTest(did=did), self.assertRaises(app.ExportError):
                app.identity_from_did(did)

    def test_roundtrip_and_source_preservation(self):
        result = self.run_export()
        exported = json.loads(Path(result["export_path"]).read_text())
        report = json.loads(Path(result["report_path"]).read_text())
        self.assertEqual(["pkcs8", "ed25519"], exported["encoding"]["content"])
        self.assertEqual(["scrypt", "xsalsa20-poly1305"], exported["encoding"]["type"])
        self.assertEqual("3", exported["encoding"]["version"])
        self.assertTrue(result["signatureVerified"] and result["tamperedMessageRejected"])
        self.assertTrue(result["source_unchanged"])
        self.assertFalse(result["new_identity"])
        self.assertEqual(self.original, self.pem.read_bytes())
        self.assertEqual(hashlib.sha256(Path(result["export_path"]).read_bytes()).hexdigest(),
                         report["sha256"])
        public_text = json.dumps(report)
        for secret in (OLD_PASSWORD, NEW_PASSWORD, VECTORS[0][0], str(self.pem)):
            self.assertNotIn(secret, public_text)
        self.assertNotIn(app.AUTHOR_DID, public_text)

    def test_second_identity_and_unicode_password(self):
        key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(VECTORS[1][0]))
        self.pem.write_bytes(key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(OLD_PASSWORD.encode())))
        self.original = self.pem.read_bytes()
        result = self.run_export(1, "Mot-de-passe-éè-🔑-二")
        self.assertEqual(fixture_did(1), result["did"])
        self.assertEqual("0x" + VECTORS[1][1], result["publicKey"])

    def test_wrong_did_refused_without_output(self):
        self.assert_error("IDENTITY_MISMATCH", fixture_did(1), self.pem, OLD_PASSWORD,
                          NEW_PASSWORD, self.output)
        self.assertEqual([], list(self.output.iterdir()))

    def test_wrong_pem_password(self):
        self.assert_error("PEM_UNLOCK_FAILED", fixture_did(), self.pem, "Wrong-Password",
                          NEW_PASSWORD, self.output)
        self.assertEqual([], list(self.output.iterdir()))

    def test_missing_and_short_passwords(self):
        self.assert_error("PASSWORD_REQUIRED", fixture_did(), self.pem, "",
                          NEW_PASSWORD, self.output)
        self.assert_error("PASSWORD_TOO_SHORT", fixture_did(), self.pem, OLD_PASSWORD,
                          "short", self.output)

    def test_plaintext_pem_refused(self):
        key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(VECTORS[0][0]))
        self.pem.write_bytes(key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        self.original = self.pem.read_bytes()
        self.assert_error("SOURCE_NOT_ENCRYPTED", fixture_did(), self.pem, OLD_PASSWORD,
                          NEW_PASSWORD, self.output)

    def test_other_key_type_refused(self):
        # Fixed public test scalar; no operational account is generated.
        key = ec.derive_private_key(1, ec.SECP256R1())
        self.pem.write_bytes(key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(OLD_PASSWORD.encode())))
        self.original = self.pem.read_bytes()
        self.assert_error("SOURCE_KEY_UNSUPPORTED", fixture_did(), self.pem, OLD_PASSWORD,
                          NEW_PASSWORD, self.output)

    def test_output_must_be_explicit_existing_and_outside_app(self):
        for output in ("", self.path/"missing", ROOT, ROOT/"tests"):
            with self.subTest(output=str(output)):
                self.assert_error("OUTPUT_INVALID", fixture_did(), self.pem, OLD_PASSWORD,
                                  NEW_PASSWORD, output)

    def test_bundle_collision_preserves_existing_file(self):
        result = self.run_export()
        bundle = Path(result["export_path"]).parent
        original = Path(result["export_path"]).read_bytes()
        class FixedDate:
            @staticmethod
            def now(tz):
                class Stamp:
                    def strftime(self, _):
                        return bundle.name[len("DID-Talisman-"):].rsplit("-",1)[0]
                return Stamp()
        with patch.object(app, "datetime", FixedDate), patch.object(app.secrets, "token_hex",
                                                               return_value=bundle.name.rsplit("-",1)[1]):
            self.assert_error("OUTPUT_INVALID", fixture_did(), self.pem, OLD_PASSWORD,
                              NEW_PASSWORD, self.output)
        self.assertEqual(original, Path(result["export_path"]).read_bytes())

    def test_helper_refuses_existing_target_and_hides_input(self):
        target = self.output/"account.json"
        target.write_text("existing-user-file")
        identity = app.identity_from_did(fixture_did())
        request = {"seed": "0x"+VECTORS[0][0], "password": NEW_PASSWORD,
                   "did": fixture_did(), "expectedAddress": identity["address"],
                   "expectedPublicKey": identity["public_key"], "outputPath": str(target)}
        completed = subprocess.run([app._node_binary(), str(ROOT/"export_ed25519.cjs")],
            input=json.dumps(request).encode(), capture_output=True, timeout=90,
            creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual(b"", completed.stdout)
        self.assertEqual(b"LOCAL_EXPORT_FAILED", completed.stderr)
        self.assertEqual("existing-user-file", target.read_text())

    def test_helper_independently_rejects_mismatched_seed(self):
        identity = app.identity_from_did(fixture_did(1))
        request = {"seed": "0x"+VECTORS[0][0], "password": NEW_PASSWORD,
                   "did": fixture_did(1), "expectedAddress": identity["address"],
                   "expectedPublicKey": identity["public_key"], "outputPath": str(self.output/"account.json")}
        with self.assertRaises(app.ExportError):
            app._run_helper(app._node_binary(), request)
        self.assertFalse((self.output/"account.json").exists())

    def test_missing_dependency_fails_before_export(self):
        with patch.object(app.shutil, "which", return_value=None):
            self.assert_error("DEPENDENCIES_MISSING", fixture_did(), self.pem, OLD_PASSWORD,
                              NEW_PASSWORD, self.output)
        self.assertEqual([], list(self.output.iterdir()))

    def test_gui_both_languages_without_any_private_input(self):
        import tkinter as tk
        for lang in ("fr", "en"):
            root = tk.Tk()
            root.withdraw()
            try:
                window = app.ImportWindow(root, lang)
                root.update_idletasks()
                for value in window.fields.values():
                    self.assertEqual("", value.get())
                self.assertFalse(window.consent.get())
                self.assertFalse(window.busy)
                self.assertIsNone(window.result)
                window.fields["did"].set(fixture_did())
                result = window.inspect()
                self.assertEqual(fixture_did(), result["did"])
                window.start_export()
                self.assertFalse(window.busy)  # Cannot read a file without explicit consent.
            finally:
                root.update_idletasks()
                root.destroy()

    def test_language_switch_preserves_inputs_and_feedback(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            view = app.ImportWindow(root, "fr")
            for name, value in {"did":fixture_did(), "source":"public-fixture.pem",
                                "old":OLD_PASSWORD, "new":NEW_PASSWORD, "again":NEW_PASSWORD,
                                "parent":"private-demo-folder"}.items():
                view.fields[name].set(value)
            view.consent.set(True)
            view.inspect()
            before = {name:value.get() for name,value in view.fields.items()}
            view.set_status("error", "IDENTITY_MISMATCH")
            for lang in ("en", "fr"):
                view.switch_language(lang)
                self.assertEqual(before, {name:value.get() for name,value in view.fields.items()})
                self.assertTrue(view.consent.get())
                self.assertEqual(app.TEXT[lang]["create"], view.create_button.cget("text"))
                self.assertEqual(app.ERRORS["IDENTITY_MISMATCH"][lang=="en"], view.status.get())
                self.assertIn(app.TEXT[lang]["address"], view.public.get())
            view.fields["did"].set(fixture_did(1))
            self.assertIsNone(view.verified_identity)
            self.assertEqual("", view.public.get())
        finally:
            root.update_idletasks()
            root.destroy()

    def test_small_window_can_reach_all_sections(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        try:
            view = app.ImportWindow(root, "en")
            view.onboarding.show("pem")
            view.onboarding.ready.set(True)
            view.onboarding.open_form()
            root.geometry("780x640")
            root.deiconify()
            root.update()
            self.assertGreater(view.canvas.bbox("all")[3], view.canvas.winfo_height())
            view.canvas.yview_moveto(1.0)
            root.update()
            self.assertGreater(view.canvas.yview()[0], 0.0)
            self.assertTrue(view.create_button.winfo_exists())
        finally:
            root.update_idletasks()
            root.destroy()

if __name__ == "__main__":
    unittest.main()
