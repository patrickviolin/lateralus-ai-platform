from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.schemas import MemorySummaries


@dataclass(frozen=True)
class SummarySnapshot:
    content: str
    covers_through_message_id: str
    revision: int


class SummaryRepository(Protocol):
    async def latest_active(self, thread_id: str) -> SummarySnapshot | None: ...

    async def save(
            self,
            *,
            thread_id: str,
            content: str,
            covers_through_message_id: str,
            model_name: str,
    ) -> SummarySnapshot: ...


class PostgresSummaryRepository:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.sessions = sessions

    async def latest_active(self, thread_id: str) -> SummarySnapshot | None:
        async with self.sessions() as session:
            result = await session.execute(
                select(MemorySummaries)
                .where(
                    MemorySummaries.thread_id == thread_id,
                    MemorySummaries.tombstoned_at.is_(None),
                )
                .order_by(MemorySummaries.revision.desc())
                .limit(1)
            )
            row = result.scalars().first()
            return self._snapshot(row) if row is not None else None

    async def save(
            self,
            *,
            thread_id: str,
            content: str,
            covers_through_message_id: str,
            model_name: str,
    ) -> SummarySnapshot:
        async with self.sessions.begin() as session:
            # Serialize revision assignment for a thread, including its first revision.
            await session.execute(select(func.pg_advisory_xact_lock(func.hashtextextended(thread_id, 0))))

            result = await session.execute(
                select(MemorySummaries).where(
                    MemorySummaries.thread_id == thread_id,
                    MemorySummaries.covers_through_message_id == covers_through_message_id,
                )
            )
            existing = result.scalars().first()
            if existing is not None:
                if existing.tombstoned_at is not None:
                    raise ValueError("Cannot reuse a tombstoned summary coverage")
                return self._snapshot(existing)

            latest_revision = await session.scalar(
                select(func.coalesce(func.max(MemorySummaries.revision), 0)).where(
                    MemorySummaries.thread_id == thread_id
                )
            )
            now = datetime.now(timezone.utc)
            row = MemorySummaries(
                thread_id=thread_id,
                revision=int(latest_revision) + 1,
                content=content,
                covers_through_message_id=covers_through_message_id,
                created_at=now,
                updated_at=now,
                model=model_name,
                prompt_version="1",
                audience="customer",
                kind="summary",
                memory_agent="conversation_summarizer",
                memory_agent_version="1",
            )
            session.add(row)
            return self._snapshot(row)

    @staticmethod
    def _snapshot(row: MemorySummaries) -> SummarySnapshot:
        return SummarySnapshot(
            content=row.content,
            covers_through_message_id=row.covers_through_message_id,
            revision=row.revision,
        )
