# Documentation Troubleshooting — Projet Bot MT5 Containerisé

Cette documentation répertorie les **problèmes rencontrés** lors de la mise en place du projet et les **solutions appliquées**.

---

## 1. Lancement de MetaTrader 5

### Symptômes
- `terminal64.exe` introuvable.
- MT5 téléchargé mais non installé.

### Causes
- Crash de Wine pendant l’installation silencieuse.
- Volume `/config` vide écrasant le préfixe Wine.

### Solutions
- Vérification de l’existence de `terminal64.exe` dans `start.sh`.
- Réinstallation automatique si absent.
- Utilisation de `xvfb-run` pour installer et lancer MT5 en mode headless.

---

## 2. Problèmes liés aux volumes

### Symptômes
- MT5 réinstallé à chaque démarrage.
- Permissions refusées dans `/config`.

### Causes
- Bind-mount d’un dossier vide de l’hôte sur `/config`.
- UID/GID incompatibles entre hôte et conteneur.

### Solutions
- Remplacer par des **volumes nommés** (gérés par Docker).
- Uniformiser `PUID`/`PGID` (par défaut 911 dans l’image linuxserver).
- Ajouter un fichier `/config/_meta/whereami.txt` pour tracer la config.

---

## 3. Crash Wine

### Symptômes
- `wine: Unhandled page fault on write access …`

### Causes
- Version obsolète de Wine (image de base dépréciée).
- Dépendances manquantes (Mono, Gecko).

### Solutions
- Installer Wine stable récent (via WineHQ).
- Installer Mono + Gecko lors du build.
- Mettre à jour l’image de base (Debian Bookworm au lieu de Bullseye).

---

## 4. Problèmes docker-compose

### Symptômes
- Différence de comportement entre `docker run` et `docker-compose up`.

### Causes
- Cache de build Docker non invalidé.
- Montage de volumes différent.

### Solutions
- Forcer rebuild :  
  ```bash
  docker compose build --no-cache
  ```
- Harmoniser la config entre `run` et `compose`.

---

## 5. Alias non fonctionnel dans le terminal

### Symptômes
- Alias `start-bot` ou `trading` non reconnu dans l’xterm.

### Causes
- xterm lancé sans `bash -l`, donc alias non chargé.

### Solutions
- Créer un **script exécutable** `/usr/local/bin/trading` :
  ```bash
  #!/bin/bash
  exec wine "C:/Program Files/Python39/python.exe" Z:/app/main.py "$@"
  ```
- Ou lancer l’xterm en forçant bash login :  
  ```bash
  xterm -ls -e bash -l
  ```

---

## 6. Port 8001 inutile

### Symptômes
- Le script attendait `nc -z localhost 8001`.
- Échec systématique.

### Causes
- MT5 n’ouvre pas de port réseau par défaut.

### Solutions
- Supprimer l’attente sur le port 8001.
- Remplacer par un test Python `MetaTrader5.initialize()`.

---

## 7. Résumé des bonnes pratiques

- **Toujours** utiliser `volumes` nommés pour `/config`.
- Tester la connexion MT5 avec `MetaTrader5.initialize()` au lieu d’un port.
- Garder un script `trading` dans `/usr/local/bin` pour simplifier le lancement du bot.
- Installer Mono/Gecko lors du build pour éviter les crashes Wine.
- Documenter les chemins via `/config/_meta/whereami.txt`.

---
