from telegram import Update
from telegram.ext import ContextTypes
from app.config import Settings
from app.keyboards.admin_menu import main_menu
from app.services.auth_service import is_admin_user, is_private_chat

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not is_private_chat(update):
        return
    user = update.effective_user
    if not user or not is_admin_user(user.id, settings):
        await update.message.reply_text("Accès refusé.")
        return
    await update.message.reply_text("✅ Admin connecté\n\nGestion du bot média :", reply_markup=main_menu())
