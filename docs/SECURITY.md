# Documentation Sécurité — Projet Bot MT5 Containerisé

Cette documentation présente les **prérequis et bonnes pratiques de sécurisation** du projet de containerisation MetaTrader 5 + Bot Python.

---

## 1. Principes de base

- **Isolation stricte** : chaque bot/MT5 tourne dans son propre conteneur, sans partage de `/config`.
- **Principe du moindre privilège** : les conteneurs tournent avec un utilisateur non-root (`PUID=911`, `PGID=911`).
- **Aucune donnée sensible en clair** : mots de passe et identifiants de comptes ne doivent pas être commités dans le repo.
- **Communication chiffrée** : usage de TLS pour toute API externe (ex : connexion broker via MT5).

---

## 2. Gestion des identifiants et secrets

### Problèmes
- Le fichier `config.py` contient les credentials MT5 en clair.

### Prérequis de sécurisation
- Ne jamais stocker les identifiants dans le repo.
- Utiliser des **variables d’environnement** dans `docker-compose.yml` :
  ```yaml
  environment:
    - MT5_ACCOUNT=10006660430
    - MT5_PASSWORD=xxxxxx
    - MT5_SERVER=MetaQuotes-Demo
  ```
- Adapter `config.py` pour lire via `os.getenv(...)`.
- Pour une approche avancée : utiliser **Docker secrets** ou **HashiCorp Vault**.

---

## 3. Volumes et données persistantes

- Utiliser des **volumes nommés** plutôt que des bind-mounts pour `/config` afin d’éviter les problèmes de permissions et de fuite de données.
- Exporter uniquement les **logs nécessaires** via un répertoire `./export` monté en lecture seule si besoin.
- Ajouter un fichier `/config/_meta/whereami.txt` pour tracer l’instance (diagnostic, pas de secret).

---

## 4. Réseau et communication

- Chaque conteneur MT5/bot est isolé dans un réseau Docker interne.
- Exposer uniquement les ports strictement nécessaires (ex : `3000` pour VNC).
- Ne pas exposer de port 8001 si aucun service n’écoute (éviter une surface d’attaque inutile).
- Si plusieurs conteneurs doivent communiquer, utiliser un **réseau bridge dédié** avec des règles précises.

---

## 5. Intégrité et mises à jour

- Toujours reconstruire l’image après mise à jour de MT5, Wine ou dépendances.
- Vérifier les signatures des binaires téléchargés (MT5 setup, Gecko, Mono).
- Appliquer les mises à jour de sécurité Debian (`apt-get upgrade`).

---

## 6. Monitoring et logs

- Centraliser les logs (MT5 + bot) dans un dossier exporté (`./export`) ou un outil externe (ELK, Grafana Loki).
- Conserver un audit trail minimal des connexions (timestamp, ID compte).

---

## 7. Check-list de sécurité avant déploiement

- [ ] Les conteneurs tournent avec un **utilisateur non-root**.
- [ ] Aucun mot de passe n’est stocké en clair dans le code.
- [ ] Tous les secrets proviennent de **variables d’environnement** ou **secrets Docker**.
- [ ] Les volumes sont isolés et protégés (`/config` → volume nommé).
- [ ] Les ports exposés sont strictement nécessaires et documentés.
- [ ] Les dépendances (Wine, MT5, Mono, Gecko) sont à jour.
- [ ] Les logs sensibles sont redirigés hors du conteneur si besoin, sans exposer les secrets.

---

## 8. Bonnes pratiques complémentaires

- Mettre en place un **pare-feu Docker** (limiter les connexions entrantes).
- Ajouter un système d’**alertes** si un conteneur crash ou redémarre trop souvent.
- Surveiller l’utilisation des ressources (CPU, RAM) pour éviter les dénis de service.
- Planifier un audit régulier de l’image et du code.

---
