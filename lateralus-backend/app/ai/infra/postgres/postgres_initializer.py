from dataclasses import dataclass

from psycopg_pool import AsyncConnectionPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import Settings


@dataclass
class PostgresResources:
    dsn: str
    pool: AsyncConnectionPool | None = None
    engine: AsyncEngine | None = None
    sessions: async_sessionmaker[AsyncSession] | None = None

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
        if self.pool is not None:
            await self.pool.close()


async def create_postgres_resources(settings: Settings) -> PostgresResources:
    if not settings.postgres_pool_enabled:
        return PostgresResources(dsn=settings.postgres_dsn)

    pool = AsyncConnectionPool(settings.postgres_dsn, open=False, close_returns=True)
    await pool.open()
    engine = create_async_engine(
        "postgresql+psycopg://",
        poolclass=NullPool,
        async_creator=pool.getconn,
    )
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    return PostgresResources(dsn=settings.postgres_dsn, pool=pool, engine=engine, sessions=sessions)
