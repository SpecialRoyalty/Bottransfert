import logging
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Message
from telegram.ext import ContextTypes

from app.config import Settings
from app.models.transfer import TransferLog
from app.services.group_service import get_target
from app.services.notification_service import notify_admins

logger = logging.getLogger(__name__)


async def log_transfer(
    session: AsyncSession,
    source_chat_id: int | None,
    target_chat_id: int | None,
    source_message_id: int | None,
    status: str,
    media_type: str | None,
    error: str | None = None,
) -> None:
    session.add(
        TransferLog(
            source_chat_id=source_chat_id,
            target_chat_id=target_chat_id,
            source_message_id=source_message_id,
            status=status,
            media_type=media_type,
            error=error,
        )
    )
    await session.commit()


async def transfer_video(
    session: AsyncSession,
    context: ContextTypes.DEFAULT_TYPE,
    settings: Settings,
    message: Message,
) -> None:
    chat = message.chat
    target = await get_target(session)

    if not target:
        await log_transfer(session, chat.id, None, message.message_id, "error", "video", "Aucun groupe cible configuré")
        await notify_admins(
            context,
            settings,
            f"⚠️ Erreur de transfert\n\nSource: {chat.title or chat.id}\nErreur: aucun groupe cible configuré.",
        )
        return

    caption = None
    if settings.forward_caption:
        caption = f"🎥 Source : {chat.title or chat.id}"

    try:
        if message.video:
            await context.bot.send_video(
                chat_id=target.chat_id,
                video=message.video.file_id,
                caption=caption,
            )
            await log_transfer(session, chat.id, target.chat_id, message.message_id, "success", "video")

        elif message.document and message.document.mime_type and message.document.mime_type.startswith("video/"):
            await context.bot.send_document(
                chat_id=target.chat_id,
                document=message.document.file_id,
                caption=caption,
            )
            await log_transfer(session, chat.id, target.chat_id, message.message_id, "success", "document_video")

    except Exception as exc:
        error_text = str(exc)
        logger.exception("Erreur de transfert: %s", error_text)
        await log_transfer(session, chat.id, target.chat_id, message.message_id, "error", "video", error_text)
        await notify_admins(
            context,
            settings,
            f"⚠️ Erreur de transfert\n\nSource: {chat.title or chat.id}\nCible: {target.title or target.chat_id}\nMessage: {message.message_id}\nErreur: {error_text}",
        )
