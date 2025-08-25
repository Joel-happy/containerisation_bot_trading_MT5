# Documentation Installation — Projet Bot MT5 Containerisé

Cette documentation décrit les étapes d’installation et de déploiement du projet MetaTrader 5 + Bot Python dans des conteneurs Docker.

---

## 1. Prérequis

- **Docker** ≥ 20.x installé sur la machine.
- **Docker Compose** ≥ v2.x installé (`docker compose version` doit fonctionner).
- Connexion Internet (pour télécharger MT5, Gecko, Mono, etc.).
- Système d’exploitation supporté : Linux, Windows (Docker Desktop), macOS.

---

## 2. Récupération du projet

Cloner le repository Git :
```bash
git clone https://github.com/Joel-happy/containerisation_bot_trading_MT5.git
cd containerisation_bot_trading_MT5
```

---

## 3. Configuration des comptes MT5

Modifier le fichier `bot-fourni/config.py` :

```python
SYMBOL = "XAUUSD"
VOLUME = 2.0

ACCOUNTS = {
    10006660430: {"password": "motdepasse", "server": "MetaQuotes-Demo"},
}
ACCOUNT_ID = list(ACCOUNTS.keys())[0]
```

⚠️ Recommandation sécurité : utiliser des **variables d’environnement** plutôt que des credentials en clair.

---

## 4. Construction de l’image

Construire l’image Docker à partir du `Dockerfile` :
```bash
docker compose build
```

Cela :
- Télécharge la base `linuxserver/baseimage-kasmvnc`.
- Installe Wine + Mono + Gecko + Python Windows.
- Copie le bot dans `/app`.
- Configure le script `start.sh`.

---

## 5. Lancement des conteneurs

Démarrer les conteneurs :
```bash
docker compose up -d
```

- Chaque service (ex: `mt5_a`, `mt5_b`, `mt5_c`) démarre un conteneur indépendant.
- MT5 est installé automatiquement (si absent) puis lancé sous Wine.
- Une interface graphique est disponible via KasmVNC sur le port mappé.

Exemple :
- `http://localhost:3070` → conteneur `mt5_a`
- `http://localhost:3071` → conteneur `mt5_b`
- `http://localhost:3072` → conteneur `mt5_c`

---

## 6. Utilisation du bot

Dans l’interface graphique du conteneur (KasmVNC), ouvrir un terminal et taper :
```bash
trading
```

Cela lance le bot (`main.py`) avec Python Windows via Wine.

Le bot propose un menu interactif :
- Affichage du prix actuel, solde, positions.
- Passer des ordres BUY/SELL.
- Clôturer toutes les positions.
- Consulter les bougies récentes.

---

## 7. Gestion et maintenance

### Vérifier les logs
```bash
docker compose logs -f mt5_a
```

### Redémarrer un conteneur
```bash
docker compose restart mt5_a
```

### Arrêter tout
```bash
docker compose down
```

### Supprimer volumes (attention, perte config/MT5)
```bash
docker compose down -v
```

---

## 8. Points importants

- Chaque conteneur a son **volume nommé** `/config` pour persister Wine et MT5.
- Si un conteneur est supprimé **avec son volume**, MT5 devra être réinstallé au prochain démarrage.
- Ne pas exposer de ports inutiles (éviter `8001` si aucun service n’écoute dessus).

---

## 9. Déploiement multi‑instances

Le `docker-compose.yml` permet plusieurs bots/MT5 simultanés :

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

Chaque service → 1 compte isolé.

---
