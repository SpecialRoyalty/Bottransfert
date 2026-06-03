from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.models.group import GroupConfig

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Groupes", callback_data="groups:list")],
        [InlineKeyboardButton("ℹ️ Infos", callback_data="info")],
        [InlineKeyboardButton("📈 Statistiques", callback_data="stats")],
        [InlineKeyboardButton("🔄 Rafraîchir", callback_data="home")],
    ])

def groups_menu(groups: list[GroupConfig]) -> InlineKeyboardMarkup:
    rows = []
    for g in groups:
        role = "📂 SOURCE" if g.role == "source" else "🎯 CIBLE" if g.role == "target" else "⚪ Non défini"
        rows.append([InlineKeyboardButton(f"{role} — {(g.title or str(g.chat_id))[:40]}", callback_data=f"group:open:{g.chat_id}")])
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="home")])
    return InlineKeyboardMarkup(rows)

def group_actions_menu(group: GroupConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Définir comme SOURCE", callback_data=f"group:set_source:{group.chat_id}")],
        [InlineKeyboardButton("🚫 Retirer des SOURCES", callback_data=f"group:remove_source:{group.chat_id}")],
        [InlineKeyboardButton("🎯 Définir comme CIBLE", callback_data=f"group:set_target:{group.chat_id}")],
        [InlineKeyboardButton("⬅️ Retour aux groupes", callback_data="groups:list")],
    ])
