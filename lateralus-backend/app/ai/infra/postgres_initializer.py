from dataclasses import dataclass
from typing import Any

from app.config import Settings


@dataclass
class PostgresResources:
    dsn: str
    pool: Any | None = None

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()


async def create_postgres_resources(settings: Settings) -> PostgresResources:
    if not settings.postgres_pool_enabled:
        return PostgresResources(dsn=settings.postgres_dsn)

    try:
        from psycopg_pool import AsyncConnectionPool
    except ImportError as exc:
        raise RuntimeError(
            "POSTGRES_POOL_ENABLED requires installing psycopg_pool."
        ) from exc

    pool = AsyncConnectionPool(settings.postgres_dsn, open=False)
    await pool.open()
    return PostgresResources(dsn=settings.postgres_dsn, pool=pool)
