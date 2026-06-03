from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models.base import Base

engine = None
SessionLocal = None

def init_engine(database_url: str) -> None:
    global engine, SessionLocal
    engine = create_async_engine(database_url, echo=False, pool_pre_ping=True)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def get_session():
    return SessionLocal
