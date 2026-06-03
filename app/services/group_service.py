from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Chat
from app.models.group import GroupConfig

async def upsert_group(session: AsyncSession, chat: Chat) -> GroupConfig:
    group = await session.get(GroupConfig, chat.id)
    title = chat.title or chat.full_name or str(chat.id)
    username = getattr(chat, "username", None)
    if group:
        group.title = title
        group.username = username
        group.is_active = True
        group.updated_at = datetime.utcnow()
        await session.commit()
        return group
    group = GroupConfig(chat_id=chat.id, title=title, username=username, role=None, is_active=True)
    session.add(group)
    await session.commit()
    return group

async def list_groups(session: AsyncSession) -> list[GroupConfig]:
    result = await session.execute(select(GroupConfig).where(GroupConfig.is_active == True).order_by(GroupConfig.title))
    return list(result.scalars().all())

async def list_sources(session: AsyncSession) -> list[GroupConfig]:
    result = await session.execute(select(GroupConfig).where(GroupConfig.role == "source", GroupConfig.is_active == True))
    return list(result.scalars().all())

async def get_target(session: AsyncSession) -> GroupConfig | None:
    result = await session.execute(select(GroupConfig).where(GroupConfig.role == "target", GroupConfig.is_active == True).limit(1))
    return result.scalar_one_or_none()

async def is_source(session: AsyncSession, chat_id: int) -> bool:
    group = await session.get(GroupConfig, chat_id)
    return bool(group and group.role == "source" and group.is_active)

async def set_source(session: AsyncSession, chat_id: int) -> None:
    group = await session.get(GroupConfig, chat_id)
    if group:
        group.role = "source"
        group.updated_at = datetime.utcnow()
        await session.commit()

async def remove_source(session: AsyncSession, chat_id: int) -> None:
    group = await session.get(GroupConfig, chat_id)
    if group and group.role == "source":
        group.role = None
        group.updated_at = datetime.utcnow()
        await session.commit()

async def set_target(session: AsyncSession, chat_id: int) -> None:
    await session.execute(update(GroupConfig).where(GroupConfig.role == "target").values(role=None, updated_at=datetime.utcnow()))
    group = await session.get(GroupConfig, chat_id)
    if group:
        group.role = "target"
        group.updated_at = datetime.utcnow()
    await session.commit()
