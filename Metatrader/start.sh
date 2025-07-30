#!/bin/bash

# Configuration variables
mt5file='/config/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe'
WINEPREFIX='/config/.wine'
wine_executable="wine"
mt5server_port="8001"
mono_url="https://dl.winehq.org/wine/wine-mono/8.0.0/wine-mono-8.0.0-x86.msi"
gecko_url="https://dl.winehq.org/wine/wine-gecko/2.47.4/wine-gecko-2.47.4-x86.msi"
python_wine_url="https://www.python.org/ftp/python/3.13.0/python-3.13.0.exe"

log() {
    echo "[MT5 Docker] $1"
}

# Check if xvfb-run is installed
if ! command -v xvfb-run &>/dev/null; then
    log "[⚠] ERROR: 'xvfb-run' not found. Please install 'xvfb' via apt in your Dockerfile."
    exit 1
fi

# 1. Installation de Mono
if [ ! -e "$WINEPREFIX/drive_c/windows/mono" ]; then
    log "[1/7] Installing Mono..."
    mkdir -p "$(dirname "$WINEPREFIX/drive_c/mono.msi")"
    curl -o "$WINEPREFIX/drive_c/mono.msi" "$mono_url"
    WINEDLLOVERRIDES=mscoree=d $wine_executable msiexec /i "$WINEPREFIX/drive_c/mono.msi" /qn
    rm -f "$WINEPREFIX/drive_c/mono.msi"
else
    log "[1/7] Mono already installed."
fi

# 1.5 Installation de Gecko
if [ ! -d "$WINEPREFIX/drive_c/windows/gecko" ]; then
    log "[1.5/7] Installing Gecko..."
    curl -o "$WINEPREFIX/drive_c/gecko.msi" "$gecko_url"
    WINEDLLOVERRIDES=mshtml=d $wine_executable msiexec /i "$WINEPREFIX/drive_c/gecko.msi" /qn
    rm -f "$WINEPREFIX/drive_c/gecko.msi"
else
    log "[1.5/7] Gecko already installed."
fi

# 2. Installation de MetaTrader 5
if [ ! -e "$mt5file" ]; then
    log "[2/7] Downloading and installing MetaTrader 5..."
    $wine_executable reg add "HKEY_CURRENT_USER\\Software\\Wine" /v Version /t REG_SZ /d "win10" /f
    curl -o "$WINEPREFIX/drive_c/mt5setup.exe" "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
    xvfb-run --auto-servernum $wine_executable "$WINEPREFIX/drive_c/mt5setup.exe" "/auto"
    sleep 5
    rm -f "$WINEPREFIX/drive_c/mt5setup.exe"
else
    log "[2/7] MetaTrader 5 already installed."
fi

# 3. Démarrage de MetaTrader
if [ -e "$mt5file" ]; then
    log "[3/7] Starting MetaTrader 5..."
    xvfb-run --auto-servernum $wine_executable "$mt5file" &
else
    log "[3/7] ERROR: MetaTrader 5 not found, skipping execution."
fi

# 4. Installer Python sous Wine
if ! $wine_executable python --version &>/dev/null; then
    log "[4/7] Installing Python in Wine..."
    curl -L "$python_wine_url" -o /tmp/python-installer.exe
    $wine_executable /tmp/python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    rm -f /tmp/python-installer.exe
else
    log "[4/7] Python already installed in Wine."
fi

# 5. Installer mt5linux dans Wine
log "[5/7] Installing Python packages in Wine..."
$wine_executable python -m pip install --upgrade pip
$wine_executable python -m pip install MetaTrader5 pymt5linux


# 6. Côté Linux : créer un environnement Python virtuel
log "[6/7] Installing required Python packages on Linux..."
$wine_executable python -m pymt5linux --host 127.0.0.1 --port "$mt5server_port" python.exe &

# Créer le venv si nécessaire
if [ ! -d "/app/balize_env" ]; then
    log "[6.1] Creating Python virtual environment in /app/balize_env..."
    python3 -m venv /app/balize_env
fi

# Définir le bon interpréteur
LINUX_PYTHON="/app/balize_env/bin/python"

# Installer les dépendances
$LINUX_PYTHON -m pip install --upgrade pip
$LINUX_PYTHON -m pip install pymt5linux pyxdg rpyc

#installer dépendances pour faire fonctionner le bot
$LINUX_PYTHON -m pip install -r /app/bot_requirements.txt

# 7. Lancer le serveur mt5linux
log "[7/7] Starting mt5linux server on port $mt5server_port..."
$LINUX_PYTHON -m mt5linux --host 0.0.0.0 -p "$mt5server_port" -w "$wine_executable" python.exe &

sleep 5
if ss -tuln | grep ":$mt5server_port" &>/dev/null; then
    log "[✔] mt5linux server is running on port $mt5server_port."
else
    log "[✖] Failed to start mt5linux server on port $mt5server_port."
fi

log "[Info] Wine version: $(wine --version)"
log "[Info] Python (Linux): $($LINUX_PYTHON --version)"
log "[Info] Python (Wine): $($wine_executable python --version)"

# 8. Lancer le bot
log "[8/7] Launching trading bot..."

$LINUX_PYTHON /app/main.py