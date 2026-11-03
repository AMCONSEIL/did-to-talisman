$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
Write-Host "Installation des dependances publiques / Installing public dependencies."
Write-Host "Aucune sauvegarde de wallet n'est lue / No wallet backup is read."
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "Installer Node.js 22 ou plus depuis nodejs.org." }
& node -e "if(Number(process.versions.node.split('.')[0])<22)process.exit(1)"
if ($LASTEXITCODE -ne 0) { throw "Node.js 22+ requis / required." }
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -c "import sys; assert sys.version_info >= (3,11)"
        if ($LASTEXITCODE -ne 0) { throw "Python 3.11+ requis / required." }
        & py -3 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c "import sys; assert sys.version_info >= (3,11)"
        if ($LASTEXITCODE -ne 0) { throw "Python 3.11+ requis / required." }
        & python -m venv .venv
    } else { throw "Installer Python 3.11+ avec Tk depuis python.org." }
    if ($LASTEXITCODE -ne 0) { throw "Creation de l'environnement Python impossible." }
}
& ".\.venv\Scripts\python.exe" -m pip install --require-hashes --only-binary=:all: -r requirements.lock.txt
if ($LASTEXITCODE -ne 0) { throw "Installation Python echouee." }
& npm.cmd ci --ignore-scripts --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw "Installation Node echouee." }
& ".\.venv\Scripts\python.exe" did_talisman.py --check-install
if ($LASTEXITCODE -ne 0) { throw "Controle d'installation echoue." }
Write-Host "Pret : LANCER.cmd (francais) ou START.cmd (English)."
