FROM ghcr.io/linuxserver/baseimage-kasmvnc:debianbullseye-8446af38-ls104

# set version label
ARG BUILD_DATE
ARG VERSION
LABEL build_version="Metatrader Docker:- ${VERSION} Build-date:- ${BUILD_DATE}"
LABEL maintainer="Balize"

ENV TITLE=Metatrader5
ENV WINEPREFIX="/config/.wine"

# Supprime la ligne backports si elle existe (pour éviter les erreurs 404)
RUN sed -i '/bullseye-backports/d' /etc/apt/sources.list

# Update package lists and upgrade packages
RUN apt-get update && apt-get upgrade -y

# Ajout de l’archi i386, installation outils et ajout WineHQ (1 seule fois)
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y \
        wget \
        curl \
        gnupg2 \
        apt-transport-https \
        ca-certificates

# Ajout clé et dépôt WineHQ (méthode moderne)
RUN curl -fsSL https://dl.winehq.org/wine-builds/winehq.key | gpg --dearmor > /usr/share/keyrings/winehq-archive.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/winehq-archive.gpg] https://dl.winehq.org/wine-builds/debian/ bullseye main" > /etc/apt/sources.list.d/winehq.list

# Installation de WineHQ stable
RUN apt-get update && apt-get install --install-recommends -y winehq-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# -- ICI tu as Wine installé --
# Installation de xvfb et iproute2
RUN apt-get update && apt-get install -y xvfb iproute2

# Compiler Python 3.13
#
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev
#

WORKDIR /opt
RUN wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz && \
    tar xzf Python-3.13.0.tgz && \
    cd Python-3.13.0 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall

RUN ln -sf /usr/local/bin/python3.13 /usr/bin/python && \
    ln -sf /usr/local/bin/python3.13 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.13 /usr/bin/pip && \
    ln -sf /usr/local/bin/pip3.13 /usr/bin/pip3



# Copier les fichiers du bot et Metatrader
COPY /bot-fourni /app/
COPY /Metatrader /Metatrader
RUN chmod +x /Metatrader/start.sh
COPY /root /

EXPOSE 3000 8001
VOLUME /config
