from app.ai.events import format_event_to_sse
from app.ai.graph import Graph
from app.ai.model import Model
from app.ai.tools.weather import get_weather


class Agent:
    def __init__(self):
        self.tools = [get_weather]
        self.model = Model(self.tools)
        self.graph = Graph(self.model).get_graph()

    async def use_agent(self, query: str):
        async for ev in self.graph.astream_events(
            {"messages": [{"role": "user", "content": query}]},
            version="v2",
            include_types=["chat_model", "tool"],
        ):
            yield format_event_to_sse(ev)
