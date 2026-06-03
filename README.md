# Telegram Media Router Bot — Photos + Vidéos

Bot Telegram silencieux dans les groupes sources.

## Il transfère quoi ?

Il transfère :
- photos Telegram natives ;
- vidéos Telegram natives ;
- documents dont le MIME type commence par `image/` ;
- documents dont le MIME type commence par `video/`.

Il ignore :
- textes ;
- audios ;
- stickers ;
- PDF ;
- autres documents non image/vidéo.

## Fonctions

- groupes sources illimités ;
- 1 groupe cible ;
- admin seulement par `ADMIN_IDS` ;
- interface admin uniquement en privé via `/start` ;
- aucun message dans les groupes sources ;
- bouton Infos avec état + stats ;
- création automatique des tables PostgreSQL ;
- retry automatique sur `Flood control exceeded` et `Timed out`.

## Variables Railway

```env
BOT_TOKEN=123456:ABC
DATABASE_URL=${{Postgres.DATABASE_URL}}
ADMIN_IDS=123456789,987654321
FORWARD_CAPTION=true
LOG_LEVEL=INFO
```

## Important BotFather

Pour voir les messages dans les groupes :

```txt
/setprivacy
Disable
```

## Lancement

```bash
python -m app.main
```
