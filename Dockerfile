FROM ghcr.io/linuxserver/baseimage-kasmvnc:debianbullseye-8446af38-ls104

ARG BUILD_DATE
ARG VERSION
LABEL build_version="Metatrader Docker:- ${VERSION} Build-date:- ${BUILD_DATE}"
LABEL maintainer="Balize"

ENV TITLE=Metatrader5
ENV WINEPREFIX="/config/.wine"

# Nettoyage backports + update/upgrade
RUN sed -i '/bullseye-backports/d' /etc/apt/sources.list
RUN apt-get update && apt-get upgrade -y

# Outils essentiels + WineHQ + Xvfb + iproute2 (pour MT5, Wine, et display virtuel)
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y wget curl gnupg2 apt-transport-https ca-certificates

RUN curl -fsSL https://dl.winehq.org/wine-builds/winehq.key | gpg --dearmor > /usr/share/keyrings/winehq-archive.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/winehq-archive.gpg] https://dl.winehq.org/wine-builds/debian/ bullseye main" > /etc/apt/sources.list.d/winehq.list

RUN apt-get update && apt-get install --install-recommends -y winehq-stable xvfb iproute2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

 # 1) Installer locales et PyXDG
RUN apt-get update && \
    apt-get install -y locales python3-pyxdg && \
    # Générer un locale UTF-8 (ajuste si tu préfères fr_FR.UTF-8)
    locale-gen en_US.UTF-8

# 2) Définir l’environnement pour utiliser UTF-8 par défaut
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONIOENCODING=utf-8
RUN apt-get update && apt-get install -y python3-pyxdg


# Copier les fichiers du bot et Metatrader
COPY /bot-fourni /app/
COPY /Metatrader /Metatrader

# Place votre script dans un service s6
COPY Metatrader/start.sh /etc/services.d/mt5/run
RUN chmod +x /etc/services.d/mt5/run

# Rends le script de démarrage exécutable (déjà à jour)
RUN chmod +x /Metatrader/start.sh


EXPOSE 3000 8001
VOLUME /config

