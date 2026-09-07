from collections.abc import AsyncIterable

from app.ai.graph import Graph
from app.ai.model import Model
from app.ai.streaming.dispatcher import StreamDispatcher
from app.ai.tools.weather import get_weather


class Agent:
    def __init__(self):
        self.tools = [get_weather]
        self.model = Model(self.tools)
        self.graph = Graph(self.model)
        self._dispatcher = StreamDispatcher.default()

    async def execute(self, query: str) -> AsyncIterable[str]:
        async for event in self.graph.astream_events(
            query,
            version="v2",
            include_types=self._dispatcher.include_types,
        ):
            yield self._dispatcher.dispatch(event)
