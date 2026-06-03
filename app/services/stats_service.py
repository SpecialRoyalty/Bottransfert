from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.group import GroupConfig
from app.models.transfer import TransferLog

async def get_stats(session: AsyncSession) -> dict:
    total_groups = await session.scalar(select(func.count()).select_from(GroupConfig))
    source_count = await session.scalar(select(func.count()).select_from(GroupConfig).where(GroupConfig.role == "source"))
    target_count = await session.scalar(select(func.count()).select_from(GroupConfig).where(GroupConfig.role == "target"))
    success_count = await session.scalar(select(func.count()).select_from(TransferLog).where(TransferLog.status == "success"))
    error_count = await session.scalar(select(func.count()).select_from(TransferLog).where(TransferLog.status == "error"))
    photo_count = await session.scalar(select(func.count()).select_from(TransferLog).where(TransferLog.status == "success", TransferLog.media_type.in_(["photo", "document_image"])))
    video_count = await session.scalar(select(func.count()).select_from(TransferLog).where(TransferLog.status == "success", TransferLog.media_type.in_(["video", "document_video"])))
    return {
        "total_groups": total_groups or 0,
        "source_count": source_count or 0,
        "target_count": target_count or 0,
        "success_count": success_count or 0,
        "error_count": error_count or 0,
        "photo_count": photo_count or 0,
        "video_count": video_count or 0,
    }
