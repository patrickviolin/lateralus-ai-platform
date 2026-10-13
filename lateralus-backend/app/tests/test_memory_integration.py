import asyncio
import os
import sys
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


@pytest.mark.skipif(os.getenv("RUN_MEMORY_INTEGRATION") != "1", reason="Requires local Redis and PostgreSQL")
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
        settings = Settings(openai_api_key="unused")
        redis = await create_redis_resources(settings)
        postgres = await create_postgres_resources(settings)
        thread_id = str(uuid4())
        try:
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
                async with postgres.sessions.begin() as session:
                    await session.execute(delete(MemorySummaries).where(MemorySummaries.thread_id == thread_id))
            finally:
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
