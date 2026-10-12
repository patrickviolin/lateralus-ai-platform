import asyncio

from app.ai.agent import Agent
from app.ai.streaming.dispatcher import StreamDispatcher


class FakeGraph:
    def __init__(self):
        self.received_input = None
        self.received_version = None
        self.received_include_types = None
        self.received_thread_id = None

    async def astream_events(self, graph_input, version, include_types, thread_id=None):
        self.received_input = graph_input
        self.received_version = version
        self.received_include_types = include_types
        self.received_thread_id = thread_id
        yield {
            "event": "on_chat_model_end",
            "run_id": "run-123",
            "data": {"content": "ok"},
        }


def test_execute_streams_formatted_graph_events():
    fake_graph = FakeGraph()
    agent = Agent.__new__(Agent)
    agent.graph = fake_graph
    agent._dispatcher = StreamDispatcher.default()

    async def collect_events():
        return [event async for event in agent.execute("Weather in Recife")]

    events = asyncio.run(collect_events())

    assert fake_graph.received_input == "Weather in Recife"
    assert fake_graph.received_version == "v2"
    assert fake_graph.received_include_types == ["chat_model", "tool"]
    assert events == [
        'event: on_chat_model_end\ndata: {"event": "on_chat_model_end", "run_id": "run-123", "data": {"content": "ok"}}\n\n'
    ]


def test_execute_passes_thread_id_to_graph():
    fake_graph = FakeGraph()
    agent = Agent.__new__(Agent)
    agent.graph = fake_graph
    agent._dispatcher = StreamDispatcher.default()

    async def collect_events():
        return [event async for event in agent.execute("And tomorrow?", thread_id="conversation-123")]

    asyncio.run(collect_events())

    assert fake_graph.received_thread_id == "conversation-123"


def test_execute_does_not_stream_summary_model_events_to_chat():
    class GraphWithSummaryEvent(FakeGraph):
        async def astream_events(self, graph_input, version, include_types, thread_id=None):
            yield {
                "event": "on_chat_model_end",
                "tags": ["memory_summary"],
                "data": {"content": "private summary"},
            }
            yield {
                "event": "on_chat_model_end",
                "data": {"content": "visible answer"},
            }

    agent = Agent.__new__(Agent)
    agent.graph = GraphWithSummaryEvent()
    agent._dispatcher = StreamDispatcher.default()

    async def collect_events():
        return [event async for event in agent.execute("Weather in Recife")]

    events = asyncio.run(collect_events())

    assert len(events) == 1
    assert "visible answer" in events[0]
    assert "private summary" not in events[0]
