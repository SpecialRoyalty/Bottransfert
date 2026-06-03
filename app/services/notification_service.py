import logging
from telegram.ext import ContextTypes
from app.config import Settings

logger = logging.getLogger(__name__)

async def notify_admins(context: ContextTypes.DEFAULT_TYPE, settings: Settings, text: str) -> None:
    for admin_id in settings.admin_ids:
        try:
            await context.bot.send_message(chat_id=admin_id, text=text)
        except Exception as exc:
            logger.warning("Notification admin impossible %s: %s", admin_id, exc)
