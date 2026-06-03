import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Message
from telegram.error import RetryAfter, TimedOut, NetworkError
from telegram.ext import ContextTypes
from app.config import Settings
from app.models.transfer import TransferLog
from app.services.group_service import get_target
from app.services.notification_service import notify_admins

logger = logging.getLogger(__name__)

async def log_transfer(session: AsyncSession, source_chat_id: int | None, target_chat_id: int | None, source_message_id: int | None, status: str, media_type: str | None, error: str | None = None) -> None:
    session.add(TransferLog(source_chat_id=source_chat_id, target_chat_id=target_chat_id, source_message_id=source_message_id, status=status, media_type=media_type, error=error))
    await session.commit()

async def _send_with_retry(send_callable, *, max_attempts: int = 5):
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await send_callable()
        except RetryAfter as exc:
            last_exc = exc
            wait_seconds = int(getattr(exc, "retry_after", 5)) + 2
            logger.warning("Flood control Telegram. Retry dans %s secondes.", wait_seconds)
            await asyncio.sleep(wait_seconds)
        except (TimedOut, NetworkError) as exc:
            last_exc = exc
            wait_seconds = min(5 * attempt, 30)
            logger.warning("Timeout/réseau. Tentative %s/%s dans %s sec: %s", attempt, max_attempts, wait_seconds, exc)
            await asyncio.sleep(wait_seconds)
    raise last_exc

def _document_kind(message: Message) -> str | None:
    if not message.document or not message.document.mime_type:
        return None
    mime = message.document.mime_type
    if mime.startswith("video/"):
        return "document_video"
    if mime.startswith("image/"):
        return "document_image"
    return None

async def transfer_media(session: AsyncSession, context: ContextTypes.DEFAULT_TYPE, settings: Settings, message: Message) -> None:
    chat = message.chat
    target = await get_target(session)
    if not target:
        await log_transfer(session, chat.id, None, message.message_id, "error", "media", "Aucun groupe cible configuré")
        await notify_admins(context, settings, f"⚠️ Erreur de transfert\n\nSource: {chat.title or chat.id}\nErreur: aucun groupe cible configuré.")
        return

    caption = f"📎 Source : {chat.title or chat.id}" if settings.forward_caption else None

    try:
        if message.photo:
            # Telegram fournit plusieurs tailles. On prend la plus grande.
            photo = message.photo[-1]
            await _send_with_retry(lambda: context.bot.send_photo(
                chat_id=target.chat_id,
                photo=photo.file_id,
                caption=caption,
                read_timeout=120,
                write_timeout=120,
                connect_timeout=30,
                pool_timeout=30,
            ))
            await log_transfer(session, chat.id, target.chat_id, message.message_id, "success", "photo")
            return

        if message.video:
            await _send_with_retry(lambda: context.bot.send_video(
                chat_id=target.chat_id,
                video=message.video.file_id,
                caption=caption,
                read_timeout=120,
                write_timeout=120,
                connect_timeout=30,
                pool_timeout=30,
            ))
            await log_transfer(session, chat.id, target.chat_id, message.message_id, "success", "video")
            return

        doc_kind = _document_kind(message)
        if doc_kind:
            await _send_with_retry(lambda: context.bot.send_document(
                chat_id=target.chat_id,
                document=message.document.file_id,
                caption=caption,
                read_timeout=120,
                write_timeout=120,
                connect_timeout=30,
                pool_timeout=30,
            ))
            await log_transfer(session, chat.id, target.chat_id, message.message_id, "success", doc_kind)
            return

    except Exception as exc:
        error_text = str(exc)
        logger.exception("Erreur de transfert après retry: %s", error_text)
        await log_transfer(session, chat.id, target.chat_id, message.message_id, "error", "media", error_text)
        await notify_admins(
            context,
            settings,
            f"⚠️ Erreur de transfert après plusieurs tentatives\n\nSource: {chat.title or chat.id}\nCible: {target.title or target.chat_id}\nMessage: {message.message_id}\nErreur: {error_text}",
        )
