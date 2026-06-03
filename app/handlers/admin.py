from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from app.config import Settings
from app.database import get_session
from app.keyboards.admin_menu import main_menu, groups_menu, group_actions_menu
from app.models.group import GroupConfig
from app.services.auth_service import is_admin_user
from app.services.group_service import list_groups, list_sources, get_target, set_source, remove_source, set_target
from app.services.stats_service import get_stats

async def _edit(update: Update, text: str, reply_markup=None) -> None:
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    q = update.callback_query
    if not q or not q.from_user or not is_admin_user(q.from_user.id, settings):
        if q: await q.answer("Accès refusé.", show_alert=True)
        return
    await q.answer()
    data = q.data or ""
    session_factory = get_session()
    async with session_factory() as session:
        if data == "home":
            return await _edit(update, "✅ Admin connecté\n\nGestion du bot média :", main_menu())
        if data == "groups:list":
            groups = await list_groups(session)
            if not groups:
                return await _edit(update, "Aucun groupe détecté. Ajoute le bot dans un groupe, puis envoie un message dans ce groupe. Le bot restera muet.", main_menu())
            return await _edit(update, "📂 Groupes détectés\n\nChoisis un groupe :", groups_menu(groups))
        if data.startswith("group:open:"):
            group = await session.get(GroupConfig, int(data.split(":")[-1]))
            if not group:
                return await _edit(update, "Groupe introuvable.", main_menu())
            return await _edit(update, f"📌 Groupe\n\nNom: {group.title}\nID: {group.chat_id}\nRôle: {group.role or 'non défini'}", group_actions_menu(group))
        if data.startswith("group:set_source:"):
            await set_source(session, int(data.split(":")[-1]))
            return await _edit(update, "✅ Groupe défini comme SOURCE.", main_menu())
        if data.startswith("group:remove_source:"):
            await remove_source(session, int(data.split(":")[-1]))
            return await _edit(update, "✅ Groupe retiré des SOURCES.", main_menu())
        if data.startswith("group:set_target:"):
            await set_target(session, int(data.split(":")[-1]))
            return await _edit(update, "✅ Groupe défini comme CIBLE. L’ancienne cible a été remplacée.", main_menu())
        if data in {"info", "stats"}:
            stats = await get_stats(session)
            sources = await list_sources(session)
            target = await get_target(session)
            started = context.application.bot_data.get("started_at")
            uptime = str(datetime.utcnow() - started).split(".")[0] if started else "inconnu"
            ready = "✅ Oui" if sources and target else "❌ Non"
            text = (
                "ℹ️ Infos bot\n\n"
                f"Actif: ✅ Oui\n"
                f"Prêt à transférer: {ready}\n"
                f"Sources: {len(sources)}\n"
                f"Cible: {target.title if target else '❌ Non configurée'}\n"
                f"Groupes détectés: {stats['total_groups']}\n"
                f"Médias transférés: {stats['success_count']}\n"
                f"Photos transférées: {stats['photo_count']}\n"
                f"Vidéos transférées: {stats['video_count']}\n"
                f"Erreurs: {stats['error_count']}\n"
                f"Uptime: {uptime}\n"
                f"Base PostgreSQL: ✅ Connectée"
            )
            return await _edit(update, text, main_menu())
        return await _edit(update, "Action inconnue.", main_menu())
