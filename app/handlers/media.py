from telegram import Update
from telegram.ext import ContextTypes
from app.config import Settings
from app.database import get_session
from app.services.group_service import upsert_group, is_source
from app.services.transfer_service import transfer_media

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message or chat.type not in {"group", "supergroup"}:
        return
    session_factory = get_session()
    async with session_factory() as session:
        await upsert_group(session, chat)
        if not await is_source(session, chat.id):
            return
        await transfer_media(session, context, settings, message)
