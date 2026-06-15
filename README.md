# ⛰️ Col Quest

Traqueur de cols de montagne cyclistes. Se connecte à Strava ou Garmin Connect, détecte automatiquement les cols gravis à partir de vos activités GPS, les enregistre en base de données PostgreSQL et les affiche sur une carte interactive Leaflet.

---

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose v2
- Un reverse proxy **Traefik** avec le réseau externe `frontend` et un point d'entrée `websecure` (HTTPS)
- Un compte **Strava** avec une application API créée (pour la connexion Strava)
- Optionnellement un compte **Garmin Connect**

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/droopy93250/Col-Quest.git
cd Col-Quest
```

### 2. Configurer l'environnement

```bash
cp .env-example .env
```

Éditez le fichier `.env` et remplissez les valeurs :

```env
DOMAIN=colquest.mondomaine.com
POSTGRES_PASSWORD=un_mot_de_passe_fort
SECRET_KEY=une_clé_secrète_aléatoire   # openssl rand -hex 32
STRAVA_CLIENT_ID=votre_client_id
STRAVA_CLIENT_SECRET=votre_client_secret
```

### 3. Lancer l'application

```bash
docker compose up -d
```

L'application sera accessible sur `https://DOMAIN` après quelques secondes.

---

## Obtenir les identifiants Strava

1. Connectez-vous sur [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Créez une nouvelle application :
   - **Nom de l'application** : Col Quest (ou n'importe quel nom)
   - **Site web** : `https://votre-domaine.com`
   - **URL de callback d'autorisation** : `https://votre-domaine.com/api/auth/strava/callback`
3. Notez le **Client ID** et le **Client Secret**
4. Renseignez-les dans votre fichier `.env`

---

## Obtenir les identifiants Garmin

Garmin Connect n'a pas d'API OAuth publique pour les particuliers. Col Quest utilise la bibliothèque `garth` qui se connecte avec vos identifiants habituels (email + mot de passe Garmin Connect).

Renseignez simplement votre email et mot de passe Garmin dans l'interface de connexion de l'application, ou dans les variables `GARMIN_EMAIL` / `GARMIN_PASSWORD` du `.env` pour une connexion automatique au démarrage.

> **Note de sécurité** : vos identifiants sont stockés côté serveur dans la base de données (session chiffrée par garth). Ils ne transitent pas en clair dans les logs.

---

## Connexion des services

1. Ouvrez `https://votre-domaine.com`
2. Cliquez sur le bouton **Connexion** en haut à droite
3. Choisissez **Strava** (redirection OAuth) ou **Garmin Connect** (email + mot de passe)
4. Une fois connecté, cliquez sur **Synchroniser** pour lancer la première synchronisation

La synchronisation automatique s'exécute chaque nuit à **2h00**.

---

## Mise à jour

```bash
git pull
docker compose build
docker compose up -d
```

---

## Synchronisation manuelle via l'API

Déclencher une synchronisation complète (Strava + Garmin) :

```bash
curl -X POST https://votre-domaine.com/api/sync/trigger
```

Synchroniser uniquement Strava :

```bash
curl -X POST https://votre-domaine.com/api/sync/strava
```

Synchroniser uniquement Garmin :

```bash
curl -X POST https://votre-domaine.com/api/sync/garmin
```

---

## Sauvegarde de la base de données

```bash
# Sauvegarder
docker exec colquest-db pg_dump -U colquest colquest > backup_$(date +%Y%m%d).sql

# Restaurer
cat backup_20240101.sql | docker exec -i colquest-db psql -U colquest colquest
```

---

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌────────────────┐
│   Traefik   │───▶│  Frontend React  │    │   PostgreSQL   │
│  (HTTPS)    │    │  + Leaflet Map   │    │   (cols +      │
│             │───▶│  FastAPI Backend │───▶│    ascents)    │
└─────────────┘    │  + APScheduler  │    └────────────────┘
                   └──────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
         Strava API            Garmin Connect
         (OAuth2)              (garth library)
```

### Détection des cols

Pour chaque activité GPS récupérée, l'algorithme vérifie si un trackpoint se trouve à moins de **600 mètres** horizontalement ET à moins de **80 mètres** d'altitude du sommet de chaque col connu. Si c'est le cas, l'ascension est enregistrée.

La base de données initiale contient **80+ cols** européens célèbres (France, Italie, Suisse, Autriche, Espagne).

---

## API Documentation

L'API FastAPI expose une documentation interactive à `https://votre-domaine.com/api/docs`.

Endpoints principaux :

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Statut du serveur |
| GET | `/cols/` | Liste tous les cols avec nombre d'ascensions |
| GET | `/cols/{id}/ascents` | Ascensions d'un col spécifique |
| GET | `/cols/ascents/all` | Toutes les ascensions (filtrable) |
| GET | `/auth/strava/login` | Lancer l'OAuth Strava |
| GET | `/auth/strava/status` | Statut connexion Strava |
| POST | `/auth/garmin/connect` | Connexion Garmin |
| POST | `/sync/trigger` | Synchronisation manuelle |

---

## Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `DOMAIN` | Domaine de l'application | Oui |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | Oui |
| `SECRET_KEY` | Clé secrète applicative | Oui |
| `STRAVA_CLIENT_ID` | ID application Strava | Si Strava |
| `STRAVA_CLIENT_SECRET` | Secret application Strava | Si Strava |
| `GARMIN_EMAIL` | Email Garmin Connect | Si Garmin |
| `GARMIN_PASSWORD` | Mot de passe Garmin | Si Garmin |
