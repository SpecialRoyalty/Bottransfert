import asyncio
import logging
from datetime import datetime

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
)

from app.config import load_settings
from app.database import init_engine, create_tables
from app.handlers.start import start
from app.handlers.admin import admin_callback
from app.handlers.media import handle_video
from app.handlers.group_events import remember_group_from_message, my_chat_member


async def post_init(app):
    await create_tables()
    app.bot_data["started_at"] = datetime.utcnow()
    logging.getLogger(__name__).info("Tables PostgreSQL vérifiées/créées.")


def build_app():
    settings = load_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    init_engine(settings.database_url)

    application = (
        ApplicationBuilder()
        .token(settings.bot_token)
        .post_init(post_init)
        .build()
    )

    application.bot_data["settings"] = settings

    # Admin privé
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(admin_callback))

    # Détection ajout/mise à jour bot dans les groupes
    application.add_handler(ChatMemberHandler(my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    # Vidéos et documents vidéo dans les groupes sources
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video), group=1)

    # Mémorisation silencieuse des groupes via messages ordinaires
    application.add_handler(MessageHandler(filters.ChatType.GROUPS, remember_group_from_message), group=2)

    return application


def main():
    app = build_app()
    logging.getLogger(__name__).info("Bot démarré en polling.")
    app.run_polling(
        allowed_updates=["message", "callback_query", "my_chat_member"],
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
