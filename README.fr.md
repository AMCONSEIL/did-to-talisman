# DID → Talisman

**Version de test publique 0.1.1 — Windows · Français / English.**

[Télécharger le ZIP](https://github.com/AMCONSEIL/did-to-talisman/archive/refs/heads/main.zip) · [Signaler un problème](https://github.com/AMCONSEIL/did-to-talisman/issues)

**Conservez votre DID existant et préparez son import dans Talisman, localement.**

[English](README.md) · [Tutoriel complet](TUTORIEL.fr.md) · [Auteur et attribution](IDENTITY.md)

L'outil transforme votre **PEM Ed25519 chiffré** en un **JSON Polkadot v3 chiffré** importable dans Talisman. Il compare la clé au DID que vous renseignez, restaure l'export et vérifie une signature avant de confirmer sa réussite.

![Fenêtre de l'outil, sans identité ni fichier personnel](docs/images/import-fr.jpg)

## Démarrer sous Windows

1. Installer [Python 3.11+ avec Tcl/Tk](https://www.python.org/downloads/windows/) et [Node.js 22+](https://nodejs.org/en/download).
2. Extraire le dossier complet, puis lancer **INSTALLER_WINDOWS.cmd**. Cette installation télécharge les dépendances publiques verrouillées ; elle ne lit aucun wallet.
3. Lancer **LANCER.cmd**. Renseigner son propre DID, sélectionner sa sauvegarde, choisir un nouveau mot de passe d'export et un dossier privé, puis créer l'export.

Les boutons **FR / EN**, en haut de la fenêtre, changent la langue sans effacer la saisie.

La conversion fonctionne hors ligne après installation. Aucun DID n'est prérempli ; aucun wallet, solde, réseau, faucet ou mineur n'est modifié.

**Première version : Windows, did:key Ed25519 en base58btc et PEM PKCS8 chiffré.** Les autres DID/formats, seeds à copier-coller, fichiers OpenSSH, wallets matériels/non exportables et PEM non chiffrés sont hors périmètre. Le DID public seul ne permet pas de récupérer sa clé.

## Résultat

Un nouveau sous-dossier **DID-Talisman-…** contient :

- **account.json** : votre clé chiffrée, à importer dans Talisman ;
- **verification.public.json** : DID, clé publique, adresse SS58 42, SHA256 et résultats des contrôles. Aucun mot de passe, seed, signature de connexion ou chemin source.

La sauvegarde d'origine est conservée. Aucun fichier existant n'est écrasé. Une erreur peut laisser un dossier non confirmé : **ne pas importer cet export**. L'outil ne supprime pas automatiquement les fichiers.

Talisman disposera d'une copie de votre clé d'identité. Choisissez un dossier privé local hors dépôt et espace partagé ; les droits Windows sont hérités de ce dossier. Python/Node ne garantissent pas l'effacement physique de la mémoire.

## Vérification et statut

Commande PowerShell : **.\.venv\Scripts\python.exe -m unittest discover -s tests -v**

Les tests utilisent deux vecteurs **publics** de la RFC 8032, jamais une clé utilisateur. Ne pas utiliser ces fixtures comme identité réelle ou pour des fonds. Voir [VALIDATION.md](VALIDATION.md).

Un test réel par un autre utilisateur dans Talisman reste nécessaire avant une version stable. Cette publication permet précisément de recueillir ces retours. Ce kit prépare le wallet ; FLOP Chat n'est pas encore inclus. Ni l'installation ni la conversion ne publient ou ne signent ce projet sous le DID de l'auteur.

Auteur : **Julien / AMCONSEIL**
DID : **did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD**
Licence : [MIT](LICENSE).

## Autres systèmes

Le code utilise Python/Tk et Node sans chemin Windows imposé. Linux/macOS : installer Python 3.11+ avec Tk et Node 22+, créer .venv avec **python3 -m venv .venv**, puis exécuter **.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements.lock.txt**, **npm ci --ignore-scripts --no-audit --no-fund**, puis **.venv/bin/python did_talisman.py --lang fr**. Ces plateformes ne sont pas encore recettées ; les lanceurs .cmd sont réservés à Windows.
