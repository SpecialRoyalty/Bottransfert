# Telegram Video Router Bot — Railway + PostgreSQL

Bot Telegram silencieux dans les groupes sources :
- détecte automatiquement les groupes où il est ajouté ;
- permet aux admins, en privé, de choisir les groupes SOURCE et le groupe CIBLE ;
- transfère les vidéos des sources vers la cible ;
- ne répond jamais dans les groupes sources ;
- notifie uniquement les admins en privé en cas d’erreur ;
- crée automatiquement les tables PostgreSQL au démarrage ;
- affiche un bouton **Infos** avec l’état et les statistiques.

## Déploiement Railway

### 1. Créer le bot Telegram

Avec BotFather :
```txt
/newbot
```

Récupère le token.

Important : pour que le bot voie les messages dans les groupes, désactive la privacy :
```txt
/setprivacy
Disable
```

### 2. Déployer sur Railway

Ajoute un service PostgreSQL Railway.

Variables d’environnement Railway :

```env
BOT_TOKEN=123456:ABC...
DATABASE_URL=${{Postgres.DATABASE_URL}}
ADMIN_IDS=123456789,987654321
FORWARD_CAPTION=true
LOG_LEVEL=INFO
```

`ADMIN_IDS` = tes IDs Telegram numériques.

Pour connaître ton ID Telegram, tu peux écrire à `@userinfobot`.

### 3. Ajouter le bot dans les groupes

Ajoute le bot :
- dans chaque groupe source ;
- dans le groupe cible.

Le bot mémorise automatiquement les groupes.

Dans les groupes, le bot reste muet.

### 4. Utiliser l’admin

Ouvre le bot en privé, puis envoie :

```txt
/start
```

Menu :
- Groupes
- Infos
- Statistiques

Dans **Groupes**, tu peux :
- définir un groupe comme source ;
- retirer une source ;
- définir un groupe comme cible.

Le bot fonctionne dès qu’il y a :
- au moins 1 source ;
- 1 cible.

## Lancer en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app/main.py
```

## Notes importantes

Le bot utilise `file_id`, donc il ne télécharge pas les vidéos. Il les renvoie via Telegram.

Le bot ne supprime jamais les messages originaux.
