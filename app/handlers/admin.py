from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from app.config import Settings
from app.database import get_session
from app.keyboards.admin_menu import main_menu, groups_menu, group_actions_menu
from app.services.auth_service import is_admin_user
from app.services.group_service import list_groups, list_sources, get_target, set_source, remove_source, set_target
from app.services.stats_service import get_stats


async def _edit_or_send(update: Update, text: str, reply_markup=None) -> None:
    query = update.callback_query
    if query:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    query = update.callback_query

    if not query or not query.from_user or not is_admin_user(query.from_user.id, settings):
        if query:
            await query.answer("Accès refusé.", show_alert=True)
        return

    await query.answer()
    data = query.data or ""

    session_factory = get_session()
    async with session_factory() as session:
        if data == "home":
            await _edit_or_send(update, "✅ Admin connecté\n\nGestion du bot vidéo :", main_menu())
            return

        if data == "groups:list":
            groups = await list_groups(session)
            if not groups:
                await _edit_or_send(
                    update,
                    "Aucun groupe détecté.\n\nAjoute le bot dans un groupe, puis envoie un message quelconque dans ce groupe. Le bot restera muet.",
                    main_menu(),
                )
                return
            await _edit_or_send(update, "📂 Groupes détectés\n\nChoisis un groupe :", groups_menu(groups))
            return

        if data.startswith("group:open:"):
            chat_id = int(data.split(":")[-1])
            group = await session.get(__import__("app.models.group", fromlist=["GroupConfig"]).GroupConfig, chat_id)
            if not group:
                await _edit_or_send(update, "Groupe introuvable.", main_menu())
                return
            role = group.role or "non défini"
            await _edit_or_send(
                update,
                f"📌 Groupe\n\nNom: {group.title}\nID: {group.chat_id}\nRôle: {role}",
                group_actions_menu(group),
            )
            return

        if data.startswith("group:set_source:"):
            chat_id = int(data.split(":")[-1])
            await set_source(session, chat_id)
            await _edit_or_send(update, "✅ Groupe défini comme SOURCE.", main_menu())
            return

        if data.startswith("group:remove_source:"):
            chat_id = int(data.split(":")[-1])
            await remove_source(session, chat_id)
            await _edit_or_send(update, "✅ Groupe retiré des SOURCES.", main_menu())
            return

        if data.startswith("group:set_target:"):
            chat_id = int(data.split(":")[-1])
            await set_target(session, chat_id)
            await _edit_or_send(update, "✅ Groupe défini comme CIBLE. L’ancienne cible a été remplacée.", main_menu())
            return

        if data in {"info", "stats"}:
            stats = await get_stats(session)
            sources = await list_sources(session)
            target = await get_target(session)

            bot_started_at = context.application.bot_data.get("started_at")
            uptime = "inconnu"
            if bot_started_at:
                delta = datetime.utcnow() - bot_started_at
                uptime = str(delta).split(".")[0]

            target_text = target.title if target else "❌ Non configurée"
            ready = "✅ Oui" if sources and target else "❌ Non"

            text = (
                "ℹ️ Infos bot\n\n"
                f"Actif: ✅ Oui\n"
                f"Prêt à transférer: {ready}\n"
                f"Sources: {len(sources)}\n"
                f"Cible: {target_text}\n"
                f"Groupes détectés: {stats['total_groups']}\n"
                f"Vidéos transférées: {stats['success_count']}\n"
                f"Erreurs: {stats['error_count']}\n"
                f"Uptime: {uptime}\n"
                f"Base PostgreSQL: ✅ Connectée"
            )
            await _edit_or_send(update, text, main_menu())
            return

        await _edit_or_send(update, "Action inconnue.", main_menu())
