from collections.abc import AsyncIterable

from app.ai.agent.tools.factory import default_tool_factory
from app.ai.agent.graph import Graph
from app.ai.agent.model import Model
from app.ai.streaming.dispatcher import StreamDispatcher


class Agent:
    def __init__(self, graph: Graph | None = None, dispatcher: StreamDispatcher | None = None, ) -> None:
        if graph is None:
            tools = default_tool_factory().create_tools()
            model = Model(tools)
            graph = Graph(model)

        self.graph = graph
        self._dispatcher = dispatcher or StreamDispatcher.default()

    async def execute(self, query: str, *, thread_id: str | None = None) -> AsyncIterable[str]:
        options = {"version": "v2", "include_types": self._dispatcher.include_types}
        if thread_id is not None:
            options["thread_id"] = thread_id

        stream = self.graph.astream_events(query, **options)
        async for event in stream:
            if "memory_summary" in event.get("tags", []):
                continue
            yield self._dispatcher.dispatch(event)
