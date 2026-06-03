import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.database import get_session
from app.services.group_service import upsert_group

logger = logging.getLogger(__name__)


async def remember_group_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat or chat.type not in {"group", "supergroup"}:
        return

    session_factory = get_session()
    async with session_factory() as session:
        await upsert_group(session, chat)


async def my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat or chat.type not in {"group", "supergroup"}:
        return

    session_factory = get_session()
    async with session_factory() as session:
        await upsert_group(session, chat)
    logger.info("Groupe détecté/mis à jour: %s %s", chat.id, chat.title)
