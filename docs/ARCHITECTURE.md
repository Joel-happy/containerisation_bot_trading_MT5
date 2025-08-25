# Documentation d’Architecture — Projet Bot MT5 Containerisé

## 1. Contexte
Ce projet vise à containeriser un bot Python qui se connecte à MetaTrader 5 (MT5).  
Chaque conteneur exécute :
- Un terminal MT5 (sous Wine + environnement graphique KasmVNC).
- Un bot Python qui interagit avec l’API `MetaTrader5`.

Objectif : permettre plusieurs instances isolées (multi‑comptes).

---

## 2. Structure des fichiers

```
.
├── Dockerfile             # Image de base Wine/KasmVNC + MT5 + Python Windows
├── docker-compose.yml     # Orchestration multi-conteneurs
├── start.sh               # Script d'init (install/launch MT5 + bot)
├── bot-fourni/
│   ├── main.py            # Interface CLI du bot (menu utilisateur)
│   ├── config.py          # Paramètres (compte, symbole, volume)
│   ├── mt5_connection.py  # Fonctions connexion/déconnexion à MT5
│   ├── mt5_data.py        # Récupération de données de marché
│   └── mt5_trading.py     # Fonctions de trading (BUY/SELL, limites, clôture)
└── Metatrader/
    └── start.sh           # Script de lancement MT5
```

---

## 3. Composants

### 3.1 Dockerfile
- Basé sur `linuxserver/baseimage-kasmvnc` (Debian + VNC).
- Installe Wine stable + Mono + Gecko.
- Installe Python Windows (pour lancer le bot côté Wine).
- Copie les sources du bot dans `/app`.
- Ajoute un alias/script `trading` pour démarrer le bot.

### 3.2 start.sh
- Initialise l’environnement Wine (`WINEPREFIX=/config/.wine`).
- Vérifie si `terminal64.exe` existe. Si non → télécharge `mt5setup.exe` et installe MT5.
- Lance MT5 via `xvfb-run` (mode headless).
- Laisse le conteneur tourner en arrière‑plan (`tail -f /dev/null`).

### 3.3 docker-compose.yml
- Déclare plusieurs services (ex: `mt5_a`, `mt5_b`, `mt5_c`).
- Chaque service :
  - `build: .` → construit à partir du Dockerfile local.
  - Volume nommé `/config` (persistance Wine/MT5).
  - Port exposé pour KasmVNC (3000, 3001, 3002…).
- Exemple :
```yaml
services:
  mt5_a:
    build: .
    ports: ["3070:3000"]
    volumes: ["mt5_a:/config"]
  mt5_b:
    build: .
    ports: ["3071:3000"]
    volumes: ["mt5_b:/config"]
volumes:
  mt5_a: {}
  mt5_b: {}
```

---

## 4. Flux d’exécution

1. **Build de l’image**
   ```bash
   docker compose build
   ```

2. **Lancement des conteneurs**
   ```bash
   docker compose up -d
   ```

3. **Dans l’interface KasmVNC :**
   - MT5 se lance automatiquement.
   - Ouvrir un terminal et taper :
     ```bash
     trading
     ```
     → démarre le bot (`main.py`) via Wine Python.

4. **Bot Python**
   - Se connecte à MT5 (`connect_to_mt5`).
   - Menu interactif (`main.py`) : affichage prix, solde, ordres BUY/SELL, clôture, historiques.

---

## 5. Points clés d’architecture

- **Isolation par conteneur** : 1 compte = 1 conteneur (via volume nommé `/config`).
- **Persistance** : `/config` est un volume → sauvegarde Wine + MT5.
- **Robustesse** : `start.sh` réinstalle MT5 si `terminal64.exe` absent.
- **Simplicité utilisateur** : commande `trading` disponible dans le terminal du conteneur.

---

## 6. Bonnes pratiques

- Utiliser `docker compose up --build` pour forcer rebuild après modification du Dockerfile.
- Éviter les `bind mounts` directs (`./config:/config`) → risque de permissions → préférer `volumes` nommés.
- Vérifier la connexion avec `MetaTrader5.initialize()` plutôt qu’un port réseau (MT5 n’ouvre pas 8001 nativement).
- Ne jamais stocker en clair les mots de passe → prévoir gestion sécurisée (Docker secrets, Vault).

---
