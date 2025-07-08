FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Préparer l'environnement + Wine + Python
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y \
    software-properties-common \
    wget \
    curl \
    unzip \
    gnupg2 \
    xvfb \
    wine64 \
    wine32 \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean

# Création d'un utilisateur non-root sécurisé
RUN useradd --create-home --shell /bin/bash trader && \
    mkdir -p /opt/app && \
    chown -R trader:trader /opt/app

# Répertoire de travail
WORKDIR /opt/app

# Copier les fichiers
COPY --chown=trader:trader bot-fourni/ ./bot
COPY --chown=trader:trader MT5/ ./mt5

# Installation des dépendances Python (via root pour éviter les problèmes de permissions)
RUN pip3 install --no-cache-dir -r ./bot/requirements.txt

# Bascule vers l'utilisateur non-root
USER trader

# Lancer MT5 avec Wine + le bot Python
CMD xvfb-run --auto-servernum wine ./mt5/terminal64.exe & python3 ./bot/main.py
