import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(value: str) -> set[int]:
    ids: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            raise ValueError(f"ADMIN_IDS contient une valeur invalide: {part}")
    return ids


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    admin_ids: set[int]
    forward_caption: bool
    log_level: str


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    database_url = os.getenv("DATABASE_URL", "").strip()
    admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
    forward_caption = os.getenv("FORWARD_CAPTION", "true").lower() in {"1", "true", "yes", "y", "on"}
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN manquant dans les variables d'environnement.")
    if not database_url:
        raise RuntimeError("DATABASE_URL manquant dans les variables d'environnement.")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if not admin_ids_raw:
        raise RuntimeError("ADMIN_IDS manquant. Exemple: ADMIN_IDS=123456789,987654321")

    return Settings(
        bot_token=bot_token,
        database_url=database_url,
        admin_ids=_parse_admin_ids(admin_ids_raw),
        forward_caption=forward_caption,
        log_level=log_level,
    )
