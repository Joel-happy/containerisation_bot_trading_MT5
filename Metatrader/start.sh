#!/bin/bash

mkdir -p /config/_meta
{
  echo "Container=$(hostname)"
  echo "Date=$(date -u)"
  echo "WINEPREFIX=${WINEPREFIX:-/config/.wine}"
} > /config/_meta/whereami.txt

# ─── Configuration XDG pour PyXDG / Openbox (évite les warnings) ───
export XDG_RUNTIME_DIR=/tmp/.xdg-runtime
mkdir -p "$XDG_RUNTIME_DIR"
echo "[ℹ] XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"

set -euo pipefail

# ─── Affichage sur KasmVNC ───
export DISPLAY=:1
echo "[ℹ] DISPLAY=$DISPLAY"

# ─── Préfixe Wine ───
export WINEPREFIX=/config/.wine
mkdir -p "$WINEPREFIX"
chown "$(id -u):$(id -g)" "$WINEPREFIX"
echo "[ℹ] WINEPREFIX=$WINEPREFIX"

# Fonction pour afficher succès/erreur
check_success() {
    local message="$1"
    local status="$2"
    if [ $? -ne 0 ]; then
        echo "{INSTALL ERROR} : $message"
        exit 1
    else
        echo "{INSTALL OK} : $status"
    fi
}

# Variables

WINEPREFIX="/config/.wine"
wine_executable="wine"
mt5file="$WINEPREFIX/drive_c/Program Files/MetaTrader 5/terminal64.exe"
python_wine_url="https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"
mt5_url="https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
bot_requirements="/app//bot_requirements.txt"
bot="/app//main.py"
PYTHON_WIN_DIR="$WINEPREFIX/drive_c/Program Files/Python39"
PYTHON_WIN_EXE="$PYTHON_WIN_DIR/python.exe"
gecko_url="https://dl.winehq.org/wine/wine-gecko/2.47.4/wine-gecko-2.47.4-x86.msi"
mono_url="https://dl.winehq.org/wine/wine-mono/8.0.0/wine-mono-8.0.0-x86.msi"

log() { echo "[MT5 Docker] $1"; }


# 1. Installer Mono et Gecko si besoin
if [ ! -e "$WINEPREFIX/drive_c/windows/mono" ]; then
    log "[1/7] Installing Mono..."
    mkdir -p "$(dirname "$WINEPREFIX/drive_c/mono.msi")"
    curl -o "$WINEPREFIX/drive_c/mono.msi" "$mono_url"
    WINEDLLOVERRIDES=mscoree=d $wine_executable msiexec /i "$WINEPREFIX/drive_c/mono.msi" /qn
    rm -f "$WINEPREFIX/drive_c/mono.msi"
else
    log "[1/7] Mono already installed."
fi

## 1.5 Installation de Gecko
if [ ! -d "$WINEPREFIX/drive_c/windows/gecko" ]; then
    log "[1.5/7] Installing Gecko..."
    curl -o "$WINEPREFIX/drive_c/gecko.msi" "$gecko_url"
    WINEDLLOVERRIDES=mshtml=d $wine_executable msiexec /i "$WINEPREFIX/drive_c/gecko.msi" /qn
    rm -f "$WINEPREFIX/drive_c/gecko.msi"
else
    log "[1.5/7] Gecko already installed."
fi

# 2. Installer MetaTrader 5 sous Wine
if [ ! -e "$mt5file" ]; then
    log "Downloading and installing MetaTrader 5..."
    $wine_executable reg add "HKEY_CURRENT_USER\\Software\\Wine" /v Version /t REG_SZ /d "win10" /f
    curl -o "$WINEPREFIX/drive_c/mt5setup.exe" "$mt5_url"
    xvfb-run --auto-servernum $wine_executable "$WINEPREFIX/drive_c/mt5setup.exe" "/auto"
    check_success "MetaTrader 5 installation failed" "[2/7] MetaTrader 5 installed successfully"
    sleep 10
    rm -f "$WINEPREFIX/drive_c/mt5setup.exe"
else
    log "MetaTrader 5 already installed."
fi

# 3. Installer Python 3.9 sous Wine
if [ ! -e "$PYTHON_WIN_EXE" ]; then
    log "Downloading and installing Python 3.9 in Wine..."
    curl -L "$python_wine_url" -o /tmp/python39-installer.exe
    $wine_executable /tmp/python39-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    rm -f /tmp/python39-installer.exe
else
    log "Python 3.9 already installed in Wine."
fi

# 4. Installer les dépendances Python sous Wine (MetaTrader5, requirements.txt)
log "Upgrading pip in Python 3.9 under Wine..."
$wine_executable "$PYTHON_WIN_EXE" -m ensurepip
$wine_executable "$PYTHON_WIN_EXE" -m pip install --upgrade pip
log "Installing MetaTrader5 Python module..."
$wine_executable "$PYTHON_WIN_EXE" -m pip install MetaTrader5

if [ -f "$bot_requirements" ]; then
    log "Installing requirements from $bot_requirements..."
    $wine_executable "$PYTHON_WIN_EXE" -m pip install -r "Z:$bot_requirements"
fi

# 5. Lancer le terminal MT5 (en background, important pour l'API !)
if [ -e "$mt5file" ]; then
    log "Starting MetaTrader 5 terminal..."

    # Lancement MT5 en arrière-plan
    $wine_executable "$mt5file" &
    MT5_PID=$!
else
    log "[ERROR] MetaTrader 5 not found, aborting."
    exit 1
fi
#
#    # Attente de l'ouverture du port RPyC (8001) ou jusqu'à 30 s max
#    log "Waiting for MetaTrader 5 RPyC service on port 8001…"
#    ATTEMPTS=0
#    until nc -z localhost 8001; do
#        if [ "$ATTEMPTS" -ge 10 ]; then
#            log "[ERROR] MT5 RPyC service did not start within expected time."
#            exit 1
#        fi
#        ATTEMPTS=$((ATTEMPTS+1))
#        sleep 3
#    done
#    log "MT5 RPyC service is up (port 8001)."
#else
#    log "[ERROR] MetaTrader 5 not found, aborting."
#    exit 1
#fi

# 6. Lancer le bot Python (dans le même Wineprefix, via Wine, avec chemin Z:)
if [ -f "$bot" ]; then
    log "Launching trading bot..."
    $wine_executable "$PYTHON_WIN_EXE" "Z:$bot" &  # Lancer le bot en arrière-plan
else
    log "[ERROR] Bot script $bot not found!"
    exit 1
fi

# 7. Démarrer KasmVNC (noVNC, VNC, Xvfb)
echo "[ℹ] Démarrage de la stack KasmVNC (noVNC, VNC, Xvfb)…"
exec /init