from collections.abc import AsyncIterable
from dataclasses import dataclass

from app.ai.agent import Agent


@dataclass(frozen=True)
class Runner:
    agent: Agent

    async def execute(self, message: str, *, thread_id: str | None = None, ) -> AsyncIterable[str]:
        async for event in self.agent.execute(message, thread_id=thread_id):
            yield event
