"""Local, bilingual orientation before any private backup is opened."""
import webbrowser

SIGNER_GUIDE_URL = "https://github.com/AMCONSEIL/technocore-local-signer/blob/main/INSTALLATION.md"
SIGNER_GUIDE_URL_FR = "https://github.com/AMCONSEIL/technocore-local-signer/blob/main/README.fr.md#installation-et-utilisation"

COPY = {
"fr": {
"back":"Retour aux choix","continue":"Continuer","tutorial":"Lire le tutoriel",
"signer_link":"J'utilisais Technocore Local Signer",
"signer_docs":"Lire le guide du signataire (GitHub)",
"ready":"J'ai mon DID complet, le PEM chiffré correspondant et son mot de passe.",
"open_form":"J'ai ces éléments — ouvrir le formulaire",
"retry_backup":"J'ai retrouvé une sauvegarde","pem_route":"J'ai un PEM et son mot de passe",
"same_identity":"Un DID est public. Il ne contient pas votre clé privée et ne crée pas automatiquement un fichier de sauvegarde.",
"start_title":"De quoi disposez-vous ?",
"start_intro":"Choisissez votre situation. Nous vous indiquerons la suite adaptée.",
"wallet_choice":"Mon identité est déjà dans un wallet",
"wallet_choice_help":"Talisman ou un autre outil vous permet déjà de signer avec cette identité.",
"backup_choice":"J'ai un fichier de sauvegarde",
"backup_choice_help":"Vous avez conservé un fichier, mais son format peut être PEM, JSON ou autre.",
"missing_choice":"J'ai seulement mon DID, ou il me manque un élément",
"missing_choice_help":"Sauvegarde introuvable ou mot de passe oublié.",
"locate_choice":"Je ne sais pas où mon identité a été créée",
"locate_choice_help":"Retrouvez d'abord le wallet ou l'outil qui conserve sa clé.",
"backup_title":"Quel type de sauvegarde avez-vous ?",
"backup_intro":"L'extension du fichier est un indice. Elle ne garantit ni son contenu ni sa compatibilité.",
"pem_choice":"Un fichier PEM chiffré",
"pem_choice_help":"Une sauvegarde Ed25519 existante, généralement avec l'extension .pem.",
"json_choice":"Un fichier JSON de wallet",
"json_choice_help":"Un export de compte Talisman ou Polkadot compatible peut être importé directement.",
"other_choice":"Un autre format, ou je ne sais pas",
"other_choice_help":"Retrouvez les instructions de l'outil d'origine avant de convertir quoi que ce soit.",
"pem_title":"Les trois éléments nécessaires",
"pem_intro":"Ce convertisseur accepte une identité did:key Ed25519 et sa sauvegarde PEM PKCS8 chiffrée.",
"did_label":"1 · Votre DID public",
"did_help":"Copiez l'identifiant complet dans le profil ou les paramètres d'identité de l'outil d'origine. Il commence ici par did:key:z6Mk… (exemple abrégé, à ne pas copier). Si vous utilisiez notre signataire, son champ DID public peut déjà le contenir. Le DID affiché en bas de cette fenêtre est celui de l’auteur, pas le vôtre.",
"pem_label":"2 · Le fichier PEM d'origine",
"pem_help":"Cherchez dans le dossier où vous aviez sauvegardé cette identité, dans vos sauvegardes privées ou sur votre support de sauvegarde. Le nom du fichier dépend de votre outil. Ce fichier contient la clé chiffrée ; il reste sur votre ordinateur. Un DID ne fournit pas automatiquement un PEM.",
"password_label":"3 · Le mot de passe de cette sauvegarde",
"password_help":"C'est le mot de passe choisi lors du chiffrement du PEM. Ce n'est pas un nouveau mot de passe à inventer ici, ni celui de GitHub, de votre messagerie ou du déverrouillage Talisman. Le nouveau mot de passe d'export sera choisi séparément dans le formulaire.",
"wallet_title":"Votre identité est déjà dans un wallet",
"wallet_intro":"Si le wallet peut signer avec la clé correspondant à votre DID, vous n'avez pas besoin de ce convertisseur.",
"wallet_label":"Vérifier l'accès existant",
"wallet_help":"Un compte en lecture seule (Watch-only) ne suffit pas : il doit pouvoir signer. Vérifiez la même clé publique ; un autre préfixe d'adresse réseau peut afficher une autre adresse pour la même clé.",
"wallet_next_label":"La suite",
"wallet_next_help":"Conservez ce wallet et utilisez-le avec un client compatible. Ce kit prépare seulement un import ; l'interface FLOP Chat n'est pas encore incluse. Si vous disposez aussi d'une sauvegarde à convertir, revenez au choix des formats.",
"json_title":"Un JSON de wallet peut s'importer directement",
"json_intro":"Vous n'avez pas besoin d'obtenir un PEM si vous avez déjà un export compatible.",
"json_label":"S'il s'agit d'un export Polkadot/Talisman compatible",
"json_help":"Dans Talisman : + / Add account → Import → JSON file. Sélectionnez votre fichier et saisissez le mot de passe de cet export, puis comparez la clé publique avec votre identité. Gardez le fichier et son mot de passe privés.",
"json_public_label":"Un JSON décrivant le DID n'est pas forcément une sauvegarde",
"json_public_help":"Un document DID peut contenir uniquement des informations publiques. Il ne permet alors pas de signer ou de récupérer une clé. Tous les exports JSON de services différents ne sont pas compatibles avec Talisman.",
"json_next_label":"Si son origine ou son format est incertain",
"json_next_help":"Consultez l'outil qui l'a exporté. Ce guide ne lit ni ne déchiffre votre JSON et ne déduit pas sa compatibilité de son extension.",
"missing_title":"Retrouver l'accès à votre identité",
"missing_intro":"Le DID public ne permet pas de récupérer la clé privée ou le mot de passe de sa sauvegarde.",
"missing_backup_label":"Si le fichier manque",
"missing_backup_help":"Retrouvez le wallet ou l'outil d'origine, puis vos sauvegardes privées ou votre support de sauvegarde. Si un wallet peut toujours signer avec cette identité, utilisez cet accès existant. Le téléchargement d'un logiciel ne contient pas votre sauvegarde personnelle.",
"missing_password_label":"Si le mot de passe manque",
"missing_password_help":"Cherchez dans l'endroit où vous l'aviez conservé ou votre gestionnaire de mots de passe, à manipuler vous-même. Notre outil et le signataire ne peuvent pas le retrouver. Vous pouvez aussi vérifier si un autre wallet garde déjà un accès utilisable à la même clé.",
"missing_next_label":"Si aucun accès utilisable n'est retrouvé",
"missing_next_help":"Suivez la procédure de récupération officielle de l'outil d'origine, si elle existe. Créer une nouvelle clé ou un autre DID ne rétablit pas l'ancienne identité. Ne partagez jamais votre sauvegarde ou vos mots de passe avec le support.",
"locate_title":"Où votre identité a-t-elle été créée ?",
"locate_intro":"Commencez par retrouver l'application ou le service utilisé lors de sa création.",
"locate_label":"Les pistes utiles",
"locate_help":"Consultez vos applications de wallet et vos propres notes de création. Regardez les rubriques Identité, Compte ou Sauvegarde de l'outil d'origine. L'identifiant est public ; l'accès à sa clé peut rester dans ce wallet, un fichier chiffré ou un autre dispositif.",
"locate_next_label":"Vous utilisiez notre signataire Technocore ?",
"locate_next_help":"Le guide ci-dessous explique où y retrouver le DID et le chemin de la clé déjà configurés. Installer une nouvelle copie ne crée ni ne restaure votre identité.",
"other_title":"Retrouver le format de l'outil d'origine",
"other_intro":"Ce convertisseur ne prend en charge que le PEM PKCS8 Ed25519 chiffré.",
"other_label":"Pour un autre export ou une clé non exportable",
"other_help":"Consultez les instructions de l'outil qui garde votre clé. Renommer un fichier en .pem ne le convertit pas. Un wallet matériel ou un autre dispositif peut devoir signer directement, sans exporter la clé.",
"other_next_label":"Conserver la même identité",
"other_next_help":"Choisissez un parcours compatible avec votre accès existant. Ne créez pas un autre compte pour essayer de retrouver le DID initial.",
"signer_title":"Si vous utilisiez Technocore Local Signer",
"signer_intro":"Il peut vous aider à localiser une identité déjà configurée. Il n'est pas nécessaire pour utiliser ce convertisseur.",
"signer_did_label":"Retrouver le DID et l'emplacement de la clé",
"signer_did_help":"Ouvrez votre installation existante avec LANCER_SIGNATAIRE.cmd. Sans signer ni publier, regardez les champs du DID public et du fichier de clé. S'ils avaient été configurés, ils indiquent vos informations. Vérifiez que le fichier existe réellement : un chemin par défaut ne prouve pas sa présence.",
"signer_password_label":"Pour le mot de passe",
"signer_password_help":"C'est celui que vous aviez choisi pour votre PEM. Le signataire ne l'enregistre pas et ne sait pas le retrouver.",
"signer_download_label":"Faut-il télécharger le dépôt ?",
"signer_download_help":"Le dépôt contient le programme et sa documentation, pas votre DID privé, votre PEM ou votre mot de passe. Un téléchargement neuf ne récupère pas une sauvegarde perdue. Le guide GitHub peut servir à comprendre une installation que vous utilisiez déjà.",
},
"en": {
"back":"Back to choices","continue":"Continue","tutorial":"Read the tutorial",
"signer_link":"I used Technocore Local Signer",
"signer_docs":"Read the signer guide (GitHub)",
"ready":"I have my complete DID, its matching encrypted PEM and the backup password.",
"open_form":"I have these items — open the form",
"retry_backup":"I found a backup","pem_route":"I have a PEM and its password",
"same_identity":"A DID is public. It contains no private key and does not automatically create a backup file.",
"start_title":"What do you already have?",
"start_intro":"Choose your situation. We will show you the appropriate next step.",
"wallet_choice":"My identity is already in a wallet",
"wallet_choice_help":"Talisman or another tool can already sign using this identity.",
"backup_choice":"I have a backup file",
"backup_choice_help":"You saved a file; its format might be PEM, JSON or something else.",
"missing_choice":"I only have my DID, or an item is missing",
"missing_choice_help":"You cannot find the backup or have forgotten its password.",
"locate_choice":"I do not know where my identity was created",
"locate_choice_help":"First locate the wallet or tool that holds its key.",
"backup_title":"What kind of backup do you have?",
"backup_intro":"A file extension is only a clue. It does not guarantee its contents or compatibility.",
"pem_choice":"An encrypted PEM file",
"pem_choice_help":"An existing Ed25519 backup, usually with a .pem extension.",
"json_choice":"A wallet JSON file",
"json_choice_help":"A compatible Talisman or Polkadot account export can be imported directly.",
"other_choice":"Another format, or I am not sure",
"other_choice_help":"Find the original tool's instructions before converting anything.",
"pem_title":"The three items you need",
"pem_intro":"This converter accepts an Ed25519 did:key and its encrypted PKCS8 PEM backup.",
"did_label":"1 · Your public DID",
"did_help":"Copy the full identifier from the original tool's identity profile or settings. Here it starts with did:key:z6Mk… (an abbreviated illustration, not a value to copy). If you used our signer, its public DID field may already contain it. The DID in this window’s footer belongs to the author, not to you.",
"pem_label":"2 · Your original PEM file",
"pem_help":"Look in the folder where you saved this identity, your private backups or backup drive. The filename depends on the original tool. This file contains the encrypted key and stays on your computer. Creating a DID does not automatically give you a PEM.",
"password_label":"3 · That backup's password",
"password_help":"This is the password chosen when the PEM was encrypted. It is not a new password to invent here, your GitHub/email password or Talisman's local unlock password. You will choose a separate new export password in the form.",
"wallet_title":"Your identity is already in a wallet",
"wallet_intro":"If the wallet can sign with the key matching your DID, you do not need this converter.",
"wallet_label":"Check your existing access",
"wallet_help":"A Watch-only account is insufficient: it must be able to sign. Check the same public key; a network address prefix can change the displayed address without changing that key.",
"wallet_next_label":"Next step",
"wallet_next_help":"Keep using that wallet with a compatible client. This kit only prepares an import; FLOP Chat is not included yet. If you also have a backup to convert, return to the format choices.",
"json_title":"A wallet JSON may import directly",
"json_intro":"You do not need to obtain a PEM if you already have a compatible export.",
"json_label":"For a compatible Polkadot/Talisman export",
"json_help":"In Talisman: + / Add account → Import → JSON file. Choose your file, enter that export's password and compare the public key with your identity. Keep the file and password private.",
"json_public_label":"A DID document in JSON is not necessarily a key backup",
"json_public_help":"A DID document may contain public information only. It cannot then sign or recover a key. JSON exports from different services are not all compatible with Talisman.",
"json_next_label":"If the origin or format is uncertain",
"json_next_help":"Consult the tool that exported it. This guide does not read or decrypt your JSON and does not infer compatibility from its extension.",
"missing_title":"Recover access to your identity",
"missing_intro":"The public DID cannot recover the private key or its backup password.",
"missing_backup_label":"If the file is missing",
"missing_backup_help":"Locate the original wallet/tool, then your private backups or backup drive. If a wallet can still sign using this identity, use that existing access. Downloading a program does not include your personal backup.",
"missing_password_label":"If the password is missing",
"missing_password_help":"Check where you stored it or your password manager yourself. This tool and our signer cannot recover it. You may also check whether another wallet already has usable access to the same key.",
"missing_next_label":"If no usable access can be recovered",
"missing_next_help":"Follow the original tool's official recovery procedure, if one exists. Creating a new key or DID does not restore the old identity. Never share backups or passwords with support.",
"locate_title":"Where was your identity created?",
"locate_intro":"First find the application or service used when it was created.",
"locate_label":"Useful places to check",
"locate_help":"Check your wallet apps and your own setup notes. Look for Identity, Account or Backup in the original tool. The identifier is public; access to its key may remain in that wallet, an encrypted file or another device.",
"locate_next_label":"Did you use our Technocore signer?",
"locate_next_help":"The guide below explains where to find an already-configured DID and key path. Installing a fresh copy does not create or restore your identity.",
"other_title":"Find the original tool's format",
"other_intro":"This converter supports encrypted Ed25519 PKCS8 PEM only.",
"other_label":"Another export format or a non-exportable key",
"other_help":"Consult the instructions of the tool holding your key. Renaming a file to .pem does not convert it. A hardware wallet or another device may need to sign directly without exporting the key.",
"other_next_label":"Preserve the same identity",
"other_next_help":"Choose a path compatible with your existing access. Do not create another account to try to recover the original DID.",
"signer_title":"If you used Technocore Local Signer",
"signer_intro":"It may help locate an already-configured identity. It is not a prerequisite for this converter.",
"signer_did_label":"Find the DID and key location",
"signer_did_help":"Open your existing installation with LANCER_SIGNATAIRE.cmd. Without signing or publishing, inspect its public DID and key-file fields. If configured previously, they contain your details. Check that the file really exists: a default path is not proof that it is present.",
"signer_password_label":"About the password",
"signer_password_help":"It is the password you chose for that PEM. The signer does not store it or recover it.",
"signer_download_label":"Should you download the repository?",
"signer_download_help":"The repository contains software and documentation, not your private identity backup, PEM or password. A fresh download cannot recover a lost backup. Its GitHub guide can explain an installation you already used.",
}}

ROUTES = {
    "start": [("wallet","wallet_choice"),("backup","backup_choice"),
              ("missing","missing_choice"),("locate","locate_choice")],
    "backup": [("pem","pem_choice"),("json","json_choice"),("other","other_choice")],
}
PARAGRAPHS = {
    "pem":[("did_label","did_help"),("pem_label","pem_help"),("password_label","password_help")],
    "wallet":[("wallet_label","wallet_help"),("wallet_next_label","wallet_next_help")],
    "json":[("json_label","json_help"),("json_public_label","json_public_help"),
            ("json_next_label","json_next_help")],
    "missing":[("missing_backup_label","missing_backup_help"),
               ("missing_password_label","missing_password_help"),
               ("missing_next_label","missing_next_help")],
    "locate":[("locate_label","locate_help"),("locate_next_label","locate_next_help")],
    "other":[("other_label","other_help"),("other_next_label","other_next_help")],
    "signer":[("signer_did_label","signer_did_help"),
              ("signer_password_label","signer_password_help"),
              ("signer_download_label","signer_download_help")],
}

class Onboarding:
    def __init__(self, app, sections):
        self.app = app
        self.sections = tuple(sections)
        self.step = "start"
        self.form_visible = False
        self.ready = app.tk.BooleanVar(value=False)
        self.wrapping = []
        self.continue_button = None
        for section in self.sections:
            section.grid_configure(row=int(section.grid_info()["row"])+1)
        self.navigation = app.ttk.Frame(app.page, style="App.TFrame")
        self.navigation.grid(row=1,column=0,sticky="ew",pady=(0,12))
        self.back_button = app.ttk.Button(self.navigation, command=lambda:self.show("start"),
                                         style="Secondary.TButton",cursor="hand2")
        self.back_button.pack(anchor="w")
        app.controls.append(self.back_button)
        self.container = app.ttk.Frame(app.page,style="App.TFrame")
        self.show("start")

    @property
    def words(self):
        return COPY[self.app.lang]

    def show(self, step):
        if self.app.busy or step not in set(ROUTES)|set(PARAGRAPHS):
            return False
        if step != self.step:
            self.ready.set(False)
        self.step, self.form_visible = step, False
        for section in self.sections:
            section.grid_remove()
        self.navigation.grid_remove()
        self.container.grid(row=1,column=0,sticky="ew")
        self.refresh()
        self.app.canvas.yview_moveto(0)
        return True

    def refresh(self):
        self.back_button.configure(text=self.words["back"])
        if self.form_visible:
            return
        for widget in self.container.winfo_children():
            widget.destroy()
        self.wrapping = []
        self.continue_button = None
        words, app = self.words, self.app
        self.container.columnconfigure(0,weight=1)
        self._label(self.container,words[self.step+"_title"],"CardTitle.TLabel",
                    row=0,pady=(0,8),background=True)
        self._label(self.container,words[self.step+"_intro"],"Intro.TLabel",
                    row=1,pady=(0,16))
        row = 2
        if self.step in ROUTES:
            for destination,key in ROUTES[self.step]:
                panel,body=self._panel(row)
                body.columnconfigure(0,weight=1)
                self._label(body,words[key],"CardTitle.TLabel",row=0)
                self._label(body,words[key+"_help"],"CardHint.TLabel",row=1,pady=(6,12))
                app.ttk.Button(body,text=words["continue"],style="Secondary.TButton",
                               cursor="hand2",command=lambda value=destination:self.show(value)).grid(
                                   row=2,column=0,sticky="w")
                row+=1
            self._label(self.container,words["same_identity"],"Intro.TLabel",row=row,pady=(8,16))
            row+=1
        else:
            for title,body_key in PARAGRAPHS[self.step]:
                panel,body=self._panel(row)
                self._label(body,words[title],"Field.TLabel",row=0)
                self._label(body,words[body_key],"CardHint.TLabel",row=1,pady=(8,0))
                row+=1
        actions=app.ttk.Frame(self.container,style="App.TFrame")
        actions.grid(row=row,column=0,sticky="ew",pady=(12,16))
        actions.columnconfigure(0,weight=1)
        action_row=0
        if self.step=="pem":
            consent=app.ttk.Frame(actions,style="App.TFrame")
            consent.grid(row=0,column=0,sticky="ew",pady=(0,12))
            consent.columnconfigure(1,weight=1)
            app.ttk.Checkbutton(consent,variable=self.ready,style="Consent.TCheckbutton",
                                command=self.update_ready).grid(row=0,column=0,sticky="n")
            label=self._label(consent,words["ready"],"App.TLabel",row=0,column=1)
            label.bind("<Button-1>",lambda event:self.toggle_ready())
            self.continue_button=app.ttk.Button(actions,text=words["open_form"],
                style="Primary.TButton",cursor="hand2",command=self.open_form)
            self.continue_button.grid(row=1,column=0,sticky="ew",pady=(0,12))
            self.update_ready()
            action_row=2
        buttons=[]
        if self.step=="signer":
            buttons.append(("signer_docs",lambda:webbrowser.open(SIGNER_GUIDE_URL if self.app.lang=="en" else SIGNER_GUIDE_URL_FR)))
            buttons.append(("pem_route",lambda:self.show("pem")))
        elif self.step in ("wallet","json"):
            buttons.append(("tutorial",app.open_guide))
            buttons.append(("retry_backup",lambda:self.show("backup")))
        elif self.step in ("missing","locate","other"):
            buttons.append(("signer_link",lambda:self.show("signer")))
            buttons.append(("retry_backup",lambda:self.show("backup")))
        else:
            buttons.append(("signer_link",lambda:self.show("signer")))
        if self.step!="start":
            buttons.append(("back",lambda:self.show("start")))
        for key,command in buttons:
            app.ttk.Button(actions,text=words[key],style="Secondary.TButton",
                           cursor="hand2",command=command).grid(
                               row=action_row,column=0,sticky="w",pady=(0,8))
            action_row+=1
        self.resize(self.app.canvas.winfo_width())

    def _panel(self,row):
        app=self.app
        panel=app.tk.Frame(self.container,background=app.COLORS["card"],
                          highlightbackground=app.COLORS["border"],highlightthickness=1)
        panel.grid(row=row,column=0,sticky="ew",pady=(0,12))
        body=app.ttk.Frame(panel,style="Card.TFrame",padding=20)
        body.pack(fill="both",expand=True)
        body.columnconfigure(0,weight=1)
        return panel,body

    def _label(self,parent,text,style,row,column=0,pady=0,background=False):
        if background:
            widget=self.app.ttk.Label(parent,text=text,style="App.TLabel",
                                       font=("Segoe UI",18,"bold"),wraplength=900)
        else:
            widget=self.app.ttk.Label(parent,text=text,style=style,wraplength=900,
                                     justify="left")
        widget.grid(row=row,column=column,sticky="w",pady=pady)
        self.wrapping.append(widget)
        return widget

    def resize(self,width):
        for widget in self.wrapping:
            widget.configure(wraplength=max(380,width-128))

    def toggle_ready(self):
        self.ready.set(not self.ready.get())
        self.update_ready()

    def update_ready(self):
        if self.continue_button is not None:
            self.continue_button.state(["!disabled"] if self.ready.get() else ["disabled"])

    def open_form(self):
        if self.app.busy or self.step!="pem" or not self.ready.get():
            return False
        self.container.grid_remove()
        for section in self.sections:
            section.grid()
        self.navigation.grid()
        self.form_visible=True
        self.step="form"
        self.app.canvas.yview_moveto(0)
        return True
