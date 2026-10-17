import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage
from sqlalchemy import delete

from app.ai.agent.graph import Graph
from app.ai.infra.postgres.postgres_initializer import create_postgres_resources
from app.ai.infra.postgres.summary_repository import PostgresSummaryRepository
from app.ai.infra.redis_initializer import create_redis_resources
from app.config import Settings
from app.domain.schemas import MemorySummaries


TEST_POSTGRES_URL = "postgresql://root:root@localhost:55432/lateralus_test_db"
TEST_REDIS_URL = "redis://localhost:56379"
MIGRATIONS = (
    "001_memory_summaries.sql",
    "002_memory_summaries_coverage_unique.sql",
)


def integration_settings() -> Settings:
    postgres_url = os.getenv("TEST_POSTGRES_URL", TEST_POSTGRES_URL)
    redis_url = os.getenv("TEST_REDIS_URL", TEST_REDIS_URL)
    app_postgres_url = os.getenv("POSTGRES_URL", Settings.postgres_dsn)
    app_redis_url = os.getenv("REDIS_URL", Settings.redis_url)

    test_postgres = urlsplit(postgres_url)
    app_postgres = urlsplit(app_postgres_url)
    if test_postgres.path != "/lateralus_test_db":
        raise ValueError("Integration tests require the lateralus_test_db database")
    if (test_postgres.hostname, test_postgres.port, test_postgres.path) == (
        app_postgres.hostname, app_postgres.port, app_postgres.path
    ):
        raise ValueError("Integration tests cannot use the application PostgreSQL database")

    test_redis = urlsplit(redis_url)
    app_redis = urlsplit(app_redis_url)
    if (test_redis.hostname, test_redis.port, test_redis.path or "/0") == (
        app_redis.hostname, app_redis.port, app_redis.path or "/0"
    ):
        raise ValueError("Integration tests cannot use the application Redis database")

    return Settings(openai_api_key="unused", postgres_dsn=postgres_url, redis_url=redis_url)


async def apply_test_migrations(postgres) -> None:
    scripts = Path(__file__).resolve().parents[2] / "scripts" / "sql"
    async with postgres.engine.begin() as connection:
        for filename in MIGRATIONS:
            await connection.exec_driver_sql((scripts / filename).read_text(encoding="utf-8"))


def test_integration_settings_reject_application_databases(monkeypatch):
    monkeypatch.setenv("POSTGRES_URL", "postgresql://root:root@localhost:55432/lateralus_test_db")
    with pytest.raises(ValueError, match="application PostgreSQL"):
        integration_settings()

    monkeypatch.setenv("POSTGRES_URL", Settings.postgres_dsn)
    monkeypatch.setenv("REDIS_URL", TEST_REDIS_URL)
    with pytest.raises(ValueError, match="application Redis"):
        integration_settings()


@pytest.mark.skipif(os.getenv("RUN_MEMORY_INTEGRATION") != "1", reason="Requires dedicated test Redis and PostgreSQL")
def test_redis_checkpoint_and_postgres_summary_across_turns():
    class FakeModel:
        tools = []
        model_name = "fake-model"

        def __init__(self):
            self.seen = []

        async def summarize(self, previous_summary, messages):
            return "Saved summary of the first turn"

        async def call_model(self, state):
            self.seen.append((state.get("summary", ""), [message.content for message in state["messages"]]))
            return {"messages": [AIMessage(content="ok")]}

    async def run():
        settings = integration_settings()
        redis = await create_redis_resources(settings)
        postgres = None
        thread_id = str(uuid4())
        try:
            postgres = await create_postgres_resources(settings)
            await apply_test_migrations(postgres)
            repository = PostgresSummaryRepository(postgres.sessions)
            model = FakeModel()
            graph = Graph(model, redis.checkpointer, repository, context_window_size=25)
            first_message = "Remember this detail. " * 30
            for message in (first_message, "What did I say?"):
                async for _ in graph.astream_events(message, thread_id=thread_id):
                    pass
            snapshot = await repository.latest_active(thread_id)
            state = await graph.application_graph.aget_state({"configurable": {"thread_id": thread_id}})
            return model.seen, snapshot, state.values
        finally:
            try:
                if postgres is not None:
                    async with postgres.sessions.begin() as session:
                        await session.execute(delete(MemorySummaries).where(MemorySummaries.thread_id == thread_id))
            finally:
                if postgres is not None:
                    await postgres.close()
                await redis.close()

    # psycopg async connections require a selector loop on Windows.
    loop_factory = asyncio.SelectorEventLoop if sys.platform == "win32" else None
    seen, snapshot, state = asyncio.run(run(), loop_factory=loop_factory)

    assert seen[0][0] == ""
    assert seen[1] == ("Saved summary of the first turn", ["What did I say?"])
    assert snapshot is not None
    assert state["summary"] == snapshot.content
    assert [message.content for message in state["messages"]] == ["What did I say?", "ok"]
