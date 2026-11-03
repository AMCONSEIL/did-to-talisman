"""Local existing-identity export. No network, wallet changes or plaintext key files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import secrets
import shutil
import stat
import subprocess
import threading
from datetime import datetime, timezone

VERSION = "0.2.0"
AUTHOR_DID = "did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD"
BASE = Path(__file__).resolve().parent
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
MAX_PEM_BYTES = 65536
ERROR_CODES = {
    "DID_UNSUPPORTED", "PASSWORD_REQUIRED", "PASSWORD_TOO_SHORT", "PASSWORD_TOO_LONG",
    "SOURCE_INVALID", "SOURCE_NOT_ENCRYPTED", "SOURCE_KEY_UNSUPPORTED",
    "PEM_UNLOCK_FAILED", "IDENTITY_MISMATCH", "OUTPUT_INVALID", "SOURCE_CHANGED",
    "DEPENDENCIES_MISSING", "LOCAL_EXPORT_FAILED", "EXPORT_NOT_CONFIRMED",
}

class ExportError(Exception):
    def __init__(self, code):
        self.code = code if code in ERROR_CODES else "LOCAL_EXPORT_FAILED"
        super().__init__(self.code)

def b58encode(raw):
    number = int.from_bytes(raw, "big")
    result = ""
    while number:
        number, remainder = divmod(number, 58)
        result = ALPHABET[remainder] + result
    return "1" * (len(raw) - len(raw.lstrip(b"\0"))) + result

def identity_from_did(did):
    """Only canonical base58btc did:key with the Ed25519 multicodec (0xed01)."""
    if not isinstance(did, str) or not did.startswith("did:key:z") or len(did) > 100:
        raise ExportError("DID_UNSUPPORTED")
    text = did[9:]
    try:
        number = 0
        for character in text:
            number = number * 58 + ALPHABET.index(character)
        raw = number.to_bytes((number.bit_length() + 7) // 8, "big")
        raw = b"\0" * (len(text) - len(text.lstrip("1"))) + raw
    except (ValueError, OverflowError):
        raise ExportError("DID_UNSUPPORTED") from None
    if len(raw) != 34 or raw[:2] != b"\xed\x01" or b58encode(raw) != text:
        raise ExportError("DID_UNSUPPORTED")
    public = raw[2:]
    # Generic SS58 format 42, 32-byte account and two-byte checksum.
    payload = bytes([42]) + public
    checksum = hashlib.blake2b(b"SS58PRE" + payload, digest_size=64).digest()[:2]
    return {"did": did, "public_key": "0x" + public.hex(),
            "address": b58encode(payload + checksum), "key_type": "ed25519", "ss58_format": 42}

def _node_binary():
    node = shutil.which("node")
    if not node:
        raise ExportError("DEPENDENCIES_MISSING")
    return node

def _run_helper(node, request=None, check=False):
    args = [node, str(BASE / "export_ed25519.cjs")]
    if check:
        args.append("--check")
    try:
        process = subprocess.run(
            args, input=None if check else json.dumps(request, ensure_ascii=True).encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            cwd=BASE, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        raise ExportError("DEPENDENCIES_MISSING" if check else "EXPORT_NOT_CONFIRMED") from None
    # Never relay child errors or stack traces: a dependency could include sensitive input.
    if process.returncode:
        code = "DEPENDENCIES_MISSING" if check else "LOCAL_EXPORT_FAILED"
        raise ExportError(code)
    try:
        response = json.loads(process.stdout.decode("utf-8"))
    except (UnicodeError, ValueError):
        raise ExportError("EXPORT_NOT_CONFIRMED") from None
    if not isinstance(response, dict):
        raise ExportError("EXPORT_NOT_CONFIRMED")
    return response

def check_dependencies():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        del Ed25519PrivateKey
    except ImportError:
        raise ExportError("DEPENDENCIES_MISSING") from None
    response = _run_helper(_node_binary(), check=True)
    if response.get("ready") is not True:
        raise ExportError("DEPENDENCIES_MISSING")
    return response

def export_existing(did, source_path, source_password, export_password, output_parent):
    """Explicitly called by the user's GUI action; only the selected encrypted PEM is read."""
    identity = identity_from_did(did)
    if not isinstance(source_password, str) or not source_password:
        raise ExportError("PASSWORD_REQUIRED")
    if not isinstance(export_password, str) or len(export_password) < 12:
        raise ExportError("PASSWORD_TOO_SHORT")
    if len(export_password) > 1024 or len(source_password) > 1024:
        raise ExportError("PASSWORD_TOO_LONG")
    if not str(source_path).strip() or not str(output_parent).strip():
        raise ExportError("OUTPUT_INVALID")
    source, parent = Path(source_path), Path(output_parent)
    try:
        if source.is_symlink() or not source.is_file():
            raise ExportError("SOURCE_INVALID")
        if not parent.is_dir():
            raise ExportError("OUTPUT_INVALID")
        # Select a real directory, never silently create an arbitrary parent tree.
        parent = parent.resolve(strict=True)
        if parent == BASE or BASE in parent.parents:
            raise ExportError("OUTPUT_INVALID")
        with source.open("rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise ExportError("SOURCE_INVALID")
            raw = handle.read(MAX_PEM_BYTES + 1)
    except ExportError:
        raise
    except OSError:
        raise ExportError("SOURCE_INVALID") from None
    if len(raw) > MAX_PEM_BYTES:
        raise ExportError("SOURCE_INVALID")
    if not raw.lstrip().startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-----"):
        raise ExportError("SOURCE_NOT_ENCRYPTED")
    source_hash = hashlib.sha256(raw).hexdigest()
    check_dependencies()  # Fail before decryption if the portable installation is incomplete.
    from cryptography.exceptions import UnsupportedAlgorithm
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    try:
        key = serialization.load_pem_private_key(raw, source_password.encode("utf-8"))
    except (ValueError, TypeError, UnsupportedAlgorithm):
        raise ExportError("PEM_UNLOCK_FAILED") from None
    if not isinstance(key, Ed25519PrivateKey):
        raise ExportError("SOURCE_KEY_UNSUPPORTED")
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    if "0x" + public.hex() != identity["public_key"]:
        raise ExportError("IDENTITY_MISMATCH")
    seed = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                             serialization.NoEncryption())
    bundle = parent / ("DID-Talisman-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                       + "-" + secrets.token_hex(6))
    try:
        bundle.mkdir(mode=0o700, exist_ok=False)
    except OSError:
        raise ExportError("OUTPUT_INVALID") from None
    target = bundle / "account.json"
    request = {"seed": "0x" + seed.hex(), "password": export_password,
               "did": did, "expectedPublicKey": identity["public_key"],
               "expectedAddress": identity["address"], "outputPath": str(target)}
    del key, seed, raw
    try:
        report = _run_helper(_node_binary(), request)
    finally:
        request.clear()  # Best effort only: neither Python nor Node guarantees memory erasure.
    if (report.get("address") != identity["address"]
            or report.get("publicKey") != identity["public_key"]
            or report.get("did") != did
            or report.get("signatureVerified") is not True
            or report.get("tamperedMessageRejected") is not True):
        raise ExportError("EXPORT_NOT_CONFIRMED")
    try:
        data = target.read_bytes()
        exported = json.loads(data)
        if (hashlib.sha256(data).hexdigest() != report.get("sha256")
                or exported.get("address") != identity["address"]
                or exported.get("encoding") != {"content": ["pkcs8", "ed25519"],
                      "type": ["scrypt", "xsalsa20-poly1305"], "version": "3"}):
            raise ExportError("EXPORT_NOT_CONFIRMED")
        # The source is never opened for writing; detect an external change during conversion.
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
            raise ExportError("SOURCE_CHANGED")
        report.update({"app_version": VERSION, "new_identity": False,
                       "source_unchanged": True, "bytes": len(data)})
        public_report = bundle / "verification.public.json"
        with public_report.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except ExportError:
        raise
    except (OSError, ValueError):
        raise ExportError("EXPORT_NOT_CONFIRMED") from None
    return {"export_path": str(target), "report_path": str(public_report), **report}

TEXT = {
"fr": {
"title": "DID → Talisman — import local",
"heading": "Utiliser mon DID existant dans Talisman",
"intro": "DID did:key Ed25519 + sauvegarde PEM chiffrée. La même clé est conservée.\n"
         "L'export est chiffré. Aucun appel réseau pendant la conversion.",
"did": "Votre DID public", "inspect": "Vérifier le DID",
"source": "Votre sauvegarde PEM chiffrée", "browse": "Choisir…",
"old": "Mot de passe actuel de cette sauvegarde",
"new": "Mot de passe du nouvel export JSON (12 caractères minimum)",
"again": "Confirmer le mot de passe du nouvel export",
"parent": "Dossier privé de destination (hors du dossier de l'application)",
"consent": "J'accepte de copier cette clé dans un export pour Talisman. Ma sauvegarde d'origine sera conservée.",
"create": "Créer et vérifier l'export chiffré",
"ready": "Prêt. Aucun fichier privé n'est lu avant votre clic sur Créer.",
"working": "Conversion locale et vérification de la restauration…",
"passwords": "La confirmation du nouveau mot de passe ne correspond pas.",
"consent_missing": "Confirmez la copie locale de votre clé pour préparer l'import.",
"address": "Adresse générique Substrate (SS58 42)", "public": "Clé publique",
"complete": "Export vérifié : {path}\nImport Talisman : + → Import → JSON file.\n"
            "Utilisez le mot de passe du nouvel export et comparez la clé publique.",
"success": "Export chiffré vérifié", "error": "Export non confirmé",
"open": "Ouvrir le dossier de l'export", "guide": "Ouvrir le tutoriel",
"author": AUTHOR_DID,
"close": "Conversion en cours. Attendez sa fin avant de fermer.",
},
"en": {
"title": "DID → Talisman — local import",
"heading": "Use my existing DID in Talisman",
"intro": "did:key Ed25519 + encrypted PEM backup. Your existing key is preserved.\n"
         "The export is encrypted. No network request during conversion.",
"did": "Your public DID", "inspect": "Check DID",
"source": "Your encrypted PEM backup", "browse": "Browse…",
"old": "Current password of this backup",
"new": "New JSON export password (at least 12 characters)",
"again": "Confirm the new export password",
"parent": "Private destination folder (outside the application folder)",
"consent": "I agree to copy this key into an export for Talisman. My original backup will be preserved.",
"create": "Create and verify encrypted export",
"ready": "Ready. No private file is read until you click Create.",
"working": "Local conversion and restore verification…",
"passwords": "The new password confirmation does not match.",
"consent_missing": "Confirm the local key copy before preparing the import.",
"address": "Generic Substrate address (SS58 42)", "public": "Public key",
"complete": "Verified export: {path}\nTalisman: + → Import → JSON file.\n"
            "Use the new export password and compare the public key.",
"success": "Encrypted export verified", "error": "Export not confirmed",
"open": "Open export folder", "guide": "Open tutorial",
"author": AUTHOR_DID,
"close": "Conversion is still running. Wait until it finishes before closing.",
}}
ERRORS = {
"DID_UNSUPPORTED": ("DID non pris en charge. Utilisez un did:key Ed25519 complet, sans fragment.",
                    "Unsupported DID. Use a complete Ed25519 did:key without a fragment."),
"PASSWORD_REQUIRED": ("Le mot de passe du PEM est nécessaire.", "The PEM password is required."),
"PASSWORD_TOO_SHORT": ("Le nouveau mot de passe doit comporter au moins 12 caractères.",
                       "The new password must contain at least 12 characters."),
"PASSWORD_TOO_LONG": ("Mot de passe trop long (maximum 1 024 caractères).", "Password too long (maximum 1,024 characters)."),
"SOURCE_INVALID": ("Choisissez un fichier PEM local normal, de moins de 64 Kio.", "Choose a regular local PEM file smaller than 64 KiB."),
"SOURCE_NOT_ENCRYPTED": ("La source doit être une sauvegarde PEM PKCS8 chiffrée.", "The source must be an encrypted PKCS8 PEM backup."),
"SOURCE_KEY_UNSUPPORTED": ("La clé de cette sauvegarde n'est pas Ed25519.", "This backup does not contain an Ed25519 key."),
"PEM_UNLOCK_FAILED": ("Impossible de déverrouiller le PEM : mot de passe ou format incorrect.",
                      "Cannot unlock the PEM: incorrect password or unsupported format."),
"IDENTITY_MISMATCH": ("La clé du PEM ne correspond pas au DID. Aucun export créé.",
                      "The PEM key does not match the DID. No export was created."),
"OUTPUT_INVALID": ("Choisissez un dossier existant hors du dossier de l'application.",
                    "Choose an existing folder outside the application folder."),
"SOURCE_CHANGED": ("La sauvegarde source a changé pendant le contrôle. Ne pas importer cet export.",
                    "The source backup changed during verification. Do not import this export."),
"DEPENDENCIES_MISSING": ("Installation incomplète : relancez INSTALLER_WINDOWS.cmd, puis réessayez.",
                         "Incomplete installation: run INSTALLER_WINDOWS.cmd, then try again."),
"LOCAL_EXPORT_FAILED": ("Échec local. Aucun secret affiché. Ne pas importer un export non confirmé.",
                        "Local export failed. No secret is displayed. Do not import an unconfirmed export."),
"EXPORT_NOT_CONFIRMED": ("Export non confirmé. Ne pas importer le fichier ; conservez la sauvegarde d'origine.",
                         "Export not confirmed. Do not import the file; preserve your original backup."),
}

MODERN_TEXT = {
"fr": {
    "heading": "Votre DID, dans Talisman.",
    "intro": "Préparez un import chiffré en conservant votre identité.",
    "eyebrow": "OUTIL LOCAL  /  VERSION DE TEST",
    "identity_title": "Votre identité",
    "identity_hint": "Vérifiez le DID public avant d'ouvrir votre sauvegarde.",
    "source_title": "Votre sauvegarde",
    "source_hint": "La clé existante reste sur votre ordinateur.",
    "export_title": "Votre export Talisman",
    "export_hint": "Un nouveau fichier chiffré. La même clé.",
    "did": "DID public · did:key Ed25519",
    "source": "Fichier PEM chiffré",
    "old": "Mot de passe de la sauvegarde",
    "new": "Nouveau mot de passe",
    "again": "Confirmer le mot de passe",
    "parent": "Dossier privé de destination",
    "password_hint": "12 caractères minimum. Ce mot de passe servira à l'import dans Talisman.",
    "source_note": "La sauvegarde d'origine est conservée. Aucun fichier existant n'est remplacé.",
    "local_note": "Conversion hors ligne après installation des dépendances.",
    "verification_hint": "La vérification du DID utilise uniquement des données publiques.",
    "verified": "DID vérifié",
    "address": "Adresse Substrate · SS58 42",
    "public": "Clé publique",
    "consent": "J'accepte de copier ma clé dans un export pour Talisman et de conserver ma sauvegarde d'origine.",
    "create": "Créer mon export chiffré",
    "ready": "Prêt. Votre sauvegarde sera ouverte uniquement après votre validation.",
    "guide": "Tutoriel",
    "open": "Ouvrir mon export",
    "status_title": "ÉTAT DE L'EXPORT",
    "language": "Langue",
},
"en": {
    "heading": "Your DID, in Talisman.",
    "intro": "Prepare an encrypted import while keeping your existing identity.",
    "eyebrow": "LOCAL TOOL  /  TEST VERSION",
    "identity_title": "Your identity",
    "identity_hint": "Check your public DID before opening your backup.",
    "source_title": "Your backup",
    "source_hint": "Your existing key stays on your computer.",
    "export_title": "Your Talisman export",
    "export_hint": "A new encrypted file. The same key.",
    "did": "Public DID · did:key Ed25519",
    "source": "Encrypted PEM file",
    "old": "Backup password",
    "new": "New password",
    "again": "Confirm password",
    "parent": "Private destination folder",
    "password_hint": "At least 12 characters. Use this password when importing into Talisman.",
    "source_note": "Your original backup is preserved. Existing files are never replaced.",
    "local_note": "Offline conversion after dependencies are installed.",
    "verification_hint": "Checking the DID uses public information only.",
    "verified": "DID verified",
    "address": "Substrate address · SS58 42",
    "public": "Public key",
    "consent": "I agree to copy my key into an export for Talisman and preserve my original backup.",
    "create": "Create my encrypted export",
    "ready": "Ready. Your backup is opened only after you confirm the export.",
    "guide": "Tutorial",
    "open": "Open my export",
    "status_title": "EXPORT STATUS",
    "language": "Language",
}}
for _language, _values in MODERN_TEXT.items():
    TEXT[_language].update(_values)


class ImportWindow:
    """Responsive native UI. Crypto and file operations remain in export_existing."""
    COLORS = {"background": "#F3F6FB", "card": "#FFFFFF", "ink": "#14243D",
              "muted": "#52627A", "border": "#CCD7E6", "primary": "#1D4ED8",
              "hover": "#1E40AF", "soft": "#EAF1FF", "success": "#176447",
              "error": "#A52735"}

    def __init__(self, root, lang="fr"):
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        self.root, self.tk, self.ttk = root, tk, ttk
        self.filedialog, self.messagebox = filedialog, messagebox
        self.lang, self.text = lang, TEXT[lang]
        self.busy, self.result = False, None
        self.events = queue.Queue()
        self.fields = {name: tk.StringVar() for name in ("did", "source", "old", "new", "again", "parent")}
        self.consent = tk.BooleanVar(value=False)
        self.status, self.public = tk.StringVar(), tk.StringVar()
        self.verified_identity = None
        self.status_kind, self.status_payload = "ready", None
        self.translatable = []
        self.controls = []
        self.entries = {}
        self.language_buttons = {}
        c = self.COLORS
        root.title(self.text["title"])
        root.configure(background=c["background"])
        width = min(1080, root.winfo_screenwidth() - 64)
        height = min(1000, root.winfo_screenheight() - 96)
        root.geometry(f"{width}x{height}")
        root.minsize(760, 620)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.style = ttk.Style(root)
        self.style.theme_use("clam")
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("App.TFrame", background=c["background"])
        self.style.configure("Card.TFrame", background=c["card"])
        self.style.configure("App.TLabel", background=c["background"], foreground=c["ink"])
        self.style.configure("Eyebrow.TLabel", background=c["background"], foreground=c["primary"],
                             font=("Segoe UI", 9, "bold"))
        self.style.configure("Hero.TLabel", background=c["background"], foreground=c["ink"],
                             font=("Segoe UI", 26, "bold"))
        self.style.configure("Intro.TLabel", background=c["background"], foreground=c["muted"],
                             font=("Segoe UI", 11))
        self.style.configure("CardTitle.TLabel", background=c["card"], foreground=c["ink"],
                             font=("Segoe UI", 14, "bold"))
        self.style.configure("CardHint.TLabel", background=c["card"], foreground=c["muted"],
                             font=("Segoe UI", 10))
        self.style.configure("Field.TLabel", background=c["card"], foreground=c["ink"],
                             font=("Segoe UI", 10, "bold"))
        self.style.configure("Badge.TLabel", background=c["soft"], foreground=c["primary"],
                             padding=(10, 8), font=("Segoe UI", 11, "bold"))
        self.style.configure("Public.TLabel", background=c["card"], foreground=c["muted"],
                             font=("Consolas", 9))
        self.style.configure("Footer.TLabel", background=c["background"], foreground=c["muted"],
                             font=("Consolas", 9))
        self.style.configure("Modern.TEntry", fieldbackground=c["card"], foreground=c["ink"],
                             insertcolor=c["ink"], bordercolor=c["border"], lightcolor=c["border"],
                             darkcolor=c["border"], padding=(12, 12), font=("Segoe UI", 11))
        self.style.map("Modern.TEntry", bordercolor=[("focus", c["primary"])],
                       fieldbackground=[("disabled", "#EEF2F7")])
        for name, bg, fg, active in (
            ("Primary.TButton", c["primary"], "#FFFFFF", c["hover"]),
            ("Secondary.TButton", "#FFFFFF", c["primary"], "#EDF3FF"),
            ("Language.TButton", c["background"], c["muted"], "#E3EBF7"),
            ("Selected.TButton", c["soft"], c["primary"], "#D8E6FF"),
        ):
            self.style.configure(name, background=bg, foreground=fg, padding=(16, 14),
                                 borderwidth=0 if name != "Secondary.TButton" else 1,
                                 bordercolor=c["border"], font=("Segoe UI", 10, "bold"),
                                 relief="flat", focuscolor=c["primary"])
            self.style.map(name, background=[("disabled", "#E4EAF3"), ("active", active)],
                           foreground=[("disabled", "#52627A")])
        self.style.configure("Consent.TCheckbutton", background=c["background"], padding=(4, 14))
        self.style.map("Consent.TCheckbutton", background=[("active", c["background"])])
        self.style.configure("Export.Horizontal.TProgressbar", background=c["primary"],
                             troughcolor="#E5ECF6", borderwidth=0, thickness=4)

        shell = ttk.Frame(root, style="App.TFrame")
        shell.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(shell, background=c["background"], highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(shell, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.page = ttk.Frame(self.canvas, style="App.TFrame", padding=(28, 24))
        self.page.columnconfigure(0, weight=1)
        self.page_id = self.canvas.create_window((0, 0), window=self.page, anchor="nw")
        self.page.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.resize)
        root.bind("<MouseWheel>", self.mouse_wheel)
        root.bind("<Next>", lambda event: self.canvas.yview_scroll(1, "pages"))
        root.bind("<Prior>", lambda event: self.canvas.yview_scroll(-1, "pages"))

        header = ttk.Frame(self.page, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        header.columnconfigure(0, weight=1)
        self.label(header, "eyebrow", "Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        self.label(header, "heading", "Hero.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 4))
        self.intro_label = self.label(header, "intro", "Intro.TLabel", wraplength=720)
        self.intro_label.grid(row=2, column=0, sticky="w")
        languages = ttk.Frame(header, style="App.TFrame")
        languages.grid(row=0, column=1, rowspan=2, sticky="ne")
        for column, code in enumerate(("fr", "en")):
            button = ttk.Button(languages, text=code.upper(), width=3,
                                command=lambda value=code: self.switch_language(value))
            button.grid(row=0, column=column, padx=(4, 0))
            self.language_buttons[code] = button

        self.identity_card = self.card(self.page, "01", "identity_title", "identity_hint")
        self.identity_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        identity_body = self.identity_card.body
        self.field(identity_body, "did", 0, button_key="inspect", command=self.inspect)
        self.verification_label = self.label(identity_body, "verification_hint", "CardHint.TLabel", wraplength=900)
        self.verification_label.grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.public_label = ttk.Label(identity_body, textvariable=self.public, style="Public.TLabel",
                                     wraplength=900)
        self.public_label.grid(row=3, column=0, sticky="w", pady=(6, 0))

        self.details = ttk.Frame(self.page, style="App.TFrame")
        self.details.grid(row=2, column=0, sticky="ew")
        self.details.columnconfigure(0, weight=1, uniform="cards")
        self.details.columnconfigure(1, weight=1, uniform="cards")
        self.source_card = self.card(self.details, "02", "source_title", "source_hint")
        self.export_card = self.card(self.details, "03", "export_title", "export_hint")
        self.source_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.export_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        source_body = self.source_card.body
        self.field(source_body, "source", 0, button_key="browse", command=lambda: self.browse("source"))
        self.field(source_body, "old", 2, password=True)
        self.label(source_body, "source_note", "CardHint.TLabel", wraplength=390).grid(
            row=4, column=0, sticky="w", pady=(16, 0))
        export_body = self.export_card.body
        passwords = ttk.Frame(export_body, style="Card.TFrame")
        passwords.grid(row=0, column=0, sticky="ew")
        passwords.columnconfigure(0, weight=1, uniform="password")
        passwords.columnconfigure(1, weight=1, uniform="password")
        for column, name in enumerate(("new", "again")):
            box = ttk.Frame(passwords, style="Card.TFrame")
            box.grid(row=0, column=column, sticky="ew", padx=(0, 8) if column == 0 else (8, 0))
            box.columnconfigure(0, weight=1)
            self.field(box, name, 0, password=True)
        self.label(export_body, "password_hint", "CardHint.TLabel", wraplength=390).grid(
            row=1, column=0, sticky="w", pady=(8, 12))
        self.field(export_body, "parent", 2, button_key="browse", command=lambda: self.browse("parent"))

        consent_row = ttk.Frame(self.page, style="App.TFrame")
        consent_row.grid(row=3, column=0, sticky="ew", pady=(16, 8))
        consent_row.columnconfigure(1, weight=1)
        consent = ttk.Checkbutton(consent_row, variable=self.consent, style="Consent.TCheckbutton",
                                  takefocus=True)
        consent.grid(row=0, column=0, sticky="n")
        self.controls.append(consent)
        self.consent_label = self.label(consent_row, "consent", "App.TLabel", wraplength=900, cursor="hand2")
        self.consent_label.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.consent_label.bind("<Button-1>", lambda event: self.toggle_consent())

        actions = ttk.Frame(self.page, style="App.TFrame")
        actions.grid(row=4, column=0, sticky="ew", pady=(0, 16))
        actions.columnconfigure(0, weight=1)
        self.create_button = self.button(actions, "create", self.start_export, "Primary.TButton")
        self.create_button.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.open_button = self.button(actions, "open", self.open_output, "Secondary.TButton")
        self.open_button.grid(row=0, column=1, padx=(0, 12))
        self.open_button.state(["disabled"])
        self.guide_button = self.button(actions, "guide", self.open_guide, "Secondary.TButton")
        self.guide_button.grid(row=0, column=2)

        status_frame = ttk.Frame(self.page, style="App.TFrame")
        status_frame.grid(row=5, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        self.label(status_frame, "status_title", "Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        self.status_label = ttk.Label(status_frame, textvariable=self.status, style="App.TLabel",
                                      foreground=c["muted"], wraplength=960)
        self.status_label.grid(row=1, column=0, sticky="w", pady=(6, 8))
        self.progress = ttk.Progressbar(status_frame, style="Export.Horizontal.TProgressbar", mode="indeterminate")
        self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.progress.grid_remove()
        footer = ttk.Frame(root, style="App.TFrame", padding=(28, 12))
        footer.pack(side="bottom", fill="x")
        ttk.Label(footer, text=AUTHOR_DID, style="Footer.TLabel").pack(anchor="w")
        self.fields["did"].trace_add("write", self.did_changed)
        self.switch_language(lang)
        from onboarding import Onboarding
        self.onboarding = Onboarding(self, (self.identity_card, self.details, consent_row, actions, status_frame))

    def label(self, parent, key, style, **kwargs):
        widget = self.ttk.Label(parent, text=self.text[key], style=style, **kwargs)
        self.translatable.append((widget, key))
        return widget

    def button(self, parent, key, command, style):
        widget = self.ttk.Button(parent, text=self.text[key], command=command, style=style, cursor="hand2")
        self.translatable.append((widget, key))
        self.controls.append(widget)
        return widget

    def card(self, parent, number, title, hint):
        c = self.COLORS
        outer = self.tk.Frame(parent, background=c["card"], highlightbackground=c["border"],
                              highlightthickness=1, borderwidth=0)
        content = self.ttk.Frame(outer, style="Card.TFrame", padding=20)
        content.pack(fill="both", expand=True)
        content.columnconfigure(1, weight=1)
        self.ttk.Label(content, text=number, style="Badge.TLabel").grid(row=0, column=0, rowspan=2,
                                                                            sticky="nw", padx=(0, 12))
        self.label(content, title, "CardTitle.TLabel").grid(row=0, column=1, sticky="w")
        self.label(content, hint, "CardHint.TLabel", wraplength=390).grid(row=1, column=1, sticky="w", pady=(4, 0))
        body = self.ttk.Frame(content, style="Card.TFrame")
        body.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        body.columnconfigure(0, weight=1)
        outer.body = body
        return outer

    def field(self, parent, name, row, password=False, button_key=None, command=None):
        self.label(parent, name, "Field.TLabel").grid(row=row, column=0, sticky="w", pady=(0 if row == 0 else 12, 6))
        line = self.ttk.Frame(parent, style="Card.TFrame")
        line.grid(row=row+1, column=0, sticky="ew")
        line.columnconfigure(0, weight=1)
        entry = self.ttk.Entry(line, textvariable=self.fields[name], style="Modern.TEntry",
                              font=("Segoe UI", 10), width=14, show="*" if password else "")
        entry.grid(row=0, column=0, sticky="ew")
        self.entries[name] = entry
        self.controls.append(entry)
        if button_key:
            self.button(line, button_key, command, "Secondary.TButton").grid(row=0, column=1, padx=(8, 0))

    def resize(self, event):
        self.canvas.itemconfigure(self.page_id, width=event.width)
        if hasattr(self, "onboarding"):
            self.onboarding.resize(event.width)
        self.intro_label.configure(wraplength=max(380, event.width-220))
        self.consent_label.configure(wraplength=max(400, event.width-100))
        self.status_label.configure(wraplength=max(400, event.width-72))
        self.verification_label.configure(wraplength=max(400, event.width-100))
        self.public_label.configure(wraplength=max(400, event.width-100))
        if event.width < 900:
            self.source_card.grid_configure(row=0, column=0, columnspan=2, padx=0, pady=(0, 16))
            self.export_card.grid_configure(row=1, column=0, columnspan=2, padx=0, pady=0)
        else:
            self.source_card.grid_configure(row=0, column=0, columnspan=1, padx=(0, 8), pady=0)
            self.export_card.grid_configure(row=0, column=1, columnspan=1, padx=(8, 0), pady=0)

    def mouse_wheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def toggle_consent(self):
        if not self.busy:
            self.consent.set(not self.consent.get())

    def switch_language(self, lang):
        if lang not in TEXT:
            return
        self.lang, self.text = lang, TEXT[lang]
        self.root.title(self.text["title"])
        for widget, key in self.translatable:
            widget.configure(text=self.text[key])
        for code, button in self.language_buttons.items():
            button.configure(style="Selected.TButton" if code == lang else "Language.TButton")
        self.update_public()
        self.set_status(self.status_kind, self.status_payload)
        if hasattr(self, "onboarding"):
            self.onboarding.refresh()

    def did_changed(self, *_):
        if self.verified_identity and self.fields["did"].get().strip() != self.verified_identity["did"]:
            self.verified_identity = None
            self.update_public()

    def update_public(self):
        if self.verified_identity:
            identity = self.verified_identity
            self.verification_label.configure(text=self.text["verified"], foreground=self.COLORS["success"])
            self.public_label.grid()
            self.public.set(self.text["address"] + ": " + identity["address"] + "\n"
                            + self.text["public"] + ": " + identity["public_key"])
        else:
            self.verification_label.configure(text=self.text["verification_hint"], foreground=self.COLORS["muted"])
            self.public.set("")
            self.public_label.grid_remove()

    def set_status(self, kind, payload=None):
        self.status_kind, self.status_payload = kind, payload
        if kind == "error":
            value = ERRORS.get(payload, ERRORS["LOCAL_EXPORT_FAILED"])[self.lang == "en"]
            color = self.COLORS["error"]
        elif kind == "complete":
            value = self.text["complete"].format(path=payload)
            color = self.COLORS["success"]
        else:
            value = self.text[kind]
            color = self.COLORS["muted"]
        self.status.set(value)
        self.status_label.configure(foreground=color)

    def browse(self, name):
        if name == "source":
            value = self.filedialog.askopenfilename(parent=self.root, filetypes=[("Encrypted PEM", "*.pem"), ("All", "*")])
        else:
            value = self.filedialog.askdirectory(parent=self.root, mustexist=True)
        if value:
            self.fields[name].set(value)

    def fail(self, code):
        self.set_status("error", code)
        self.messagebox.showerror(self.text["error"], self.status.get(), parent=self.root)

    def inspect(self):
        try:
            self.verified_identity = identity_from_did(self.fields["did"].get().strip())
            self.update_public()
            return self.verified_identity
        except ExportError as error:
            self.verified_identity = None
            self.update_public()
            self.fail(error.code)
            return None

    def start_export(self):
        if self.busy:
            return
        if hasattr(self, "onboarding") and not self.onboarding.form_visible:
            self.onboarding.show("start")
            return
        if not self.consent.get():
            self.set_status("consent_missing")
            return
        if self.fields["new"].get() != self.fields["again"].get():
            self.set_status("passwords")
            return
        identity = self.inspect()
        if identity is None:
            return
        values = (identity["did"], self.fields["source"].get(), self.fields["old"].get(),
                  self.fields["new"].get(), self.fields["parent"].get())
        self.busy, self.result = True, None
        self.open_button.state(["disabled"])
        self.set_status("working")
        for control in self.controls:
            control.state(["disabled"])
        self.progress.grid()
        self.progress.start(15)
        threading.Thread(target=self._worker, args=values, daemon=True).start()
        self.root.after(100, self.poll)

    def _worker(self, *values):
        try:
            self.events.put(("ok", export_existing(*values)))
        except ExportError as error:
            self.events.put(("error", error.code))
        except Exception:
            self.events.put(("error", "LOCAL_EXPORT_FAILED"))

    def poll(self):
        try:
            kind, result = self.events.get_nowait()
        except queue.Empty:
            self.root.after(100, self.poll)
            return
        for name in ("old", "new", "again"):
            self.fields[name].set("")
        self.busy = False
        self.progress.stop()
        self.progress.grid_remove()
        for control in self.controls:
            control.state(["!disabled"])
        if kind == "error":
            self.open_button.state(["disabled"])
            self.fail(result)
            return
        self.result = result
        self.open_button.state(["!disabled"])
        self.set_status("complete", result["export_path"])
        self.messagebox.showinfo(self.text["success"], self.status.get(), parent=self.root)

    def _open_path(self, path):
        if os.name == "nt":
            os.startfile(str(path))
        else:
            command = shutil.which("open" if __import__("sys").platform == "darwin" else "xdg-open")
            if command:
                subprocess.Popen([command, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def open_output(self):
        if self.result:
            self._open_path(Path(self.result["export_path"]).parent)

    def open_guide(self):
        self._open_path(BASE / ("TUTORIEL.fr.md" if self.lang == "fr" else "TUTORIAL.md"))

    def close(self):
        if self.busy:
            self.messagebox.showinfo(self.text["title"], self.text["close"], parent=self.root)
        else:
            self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=("fr", "en"), default="fr")
    parser.add_argument("--check-did", metavar="PUBLIC_DID", help="Public identity check only; opens no key.")
    parser.add_argument("--check-install", action="store_true")
    args = parser.parse_args()
    try:
        if args.check_did:
            print(json.dumps(identity_from_did(args.check_did), indent=2))
            return
        if args.check_install:
            print(json.dumps(check_dependencies(), indent=2))
            return
        import tkinter as tk
        root = tk.Tk()
        ImportWindow(root, args.lang)
        root.mainloop()
    except ExportError as error:
        print(error.code)
        raise SystemExit(1) from None

if __name__ == "__main__":
    main()
