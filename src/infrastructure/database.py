from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.settings.db import DatabaseConfig

_db_config = DatabaseConfig()

engine = create_async_engine(_db_config.url, echo=False, pool_pre_ping=True)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
