import logging
from datetime import datetime
from telegram.request import HTTPXRequest
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ChatMemberHandler, filters
from app.config import load_settings
from app.database import init_engine, create_tables
from app.handlers.start import start
from app.handlers.admin import admin_callback
from app.handlers.media import handle_media
from app.handlers.group_events import remember_group_from_message, my_chat_member

async def post_init(app):
    await create_tables()
    app.bot_data["started_at"] = datetime.utcnow()
    logging.getLogger(__name__).info("Tables PostgreSQL vérifiées/créées.")

def build_app():
    settings = load_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO), format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    init_engine(settings.database_url)

    request = HTTPXRequest(connection_pool_size=20, connect_timeout=30, read_timeout=120, write_timeout=120, pool_timeout=30)
    application = ApplicationBuilder().token(settings.bot_token).request(request).post_init(post_init).concurrent_updates(False).build()
    application.bot_data["settings"] = settings

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(admin_callback))
    application.add_handler(ChatMemberHandler(my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    # Photos + vidéos natives + documents image/vidéo. Le reste est ignoré.
    application.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.Document.IMAGE | filters.Document.VIDEO,
            handle_media
        ),
        group=1
    )
    application.add_handler(MessageHandler(filters.ChatType.GROUPS, remember_group_from_message), group=2)
    return application

def main():
    app = build_app()
    logging.getLogger(__name__).info("Bot démarré en polling.")
    app.run_polling(allowed_updates=["message", "callback_query", "my_chat_member"], drop_pending_updates=False)

if __name__ == "__main__":
    main()
