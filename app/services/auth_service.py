from telegram import Update
from app.config import Settings

def is_admin_user(user_id: int | None, settings: Settings) -> bool:
    return user_id is not None and user_id in settings.admin_ids

def is_private_chat(update: Update) -> bool:
    return bool(update.effective_chat and update.effective_chat.type == "private")
