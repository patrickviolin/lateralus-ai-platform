from typing import Protocol

from psycopg_pool import AsyncConnectionPool


class SummaryReader(Protocol):
    async def latest_active(self, thread_id: str) -> str | None: ...


class PostgresSummaryReader:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self.pool = pool

    async def latest_active(self, thread_id: str) -> str | None:
        async with self.pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT content
                    FROM memory_summaries
                    WHERE thread_id = %s AND tombstoned_at IS NULL
                    ORDER BY revision DESC
                    LIMIT 1
                    """,
                    (thread_id,),
                )
                row = await cursor.fetchone()
        return row[0] if row is not None else None
