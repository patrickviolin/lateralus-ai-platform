import asyncio

from langchain_core.messages import AIMessage
from langgraph.constants import END
from langgraph.checkpoint.memory import InMemorySaver

from app.ai.agent.graph import Graph, route
from app.ai.infra.postgres.summary_repository import SummarySnapshot


def test_route_sends_tool_calls_to_tool_node():
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_weather",
                        "args": {"city": "Recife"},
                        "id": "call-123",
                    }
                ],
            )
        ]
    }

    assert route(state) == "tools"


def test_route_ends_when_no_tool_calls_exist():
    state = {"messages": [AIMessage(content="The weather is available.")]}

    assert route(state) == END


def test_checkpointer_keeps_turns_within_their_thread():
    class EchoModel:
        tools = []

        def __init__(self):
            self.seen_turns = []

        def call_model(self, state):
            self.seen_turns.append(
                [message.content for message in state["messages"] if message.type == "human"]
            )
            return {"messages": [AIMessage(content="ok")]}

    model = EchoModel()
    graph = Graph(model, checkpointer=InMemorySaver())

    async def run_turn(message, thread_id):
        async for _ in graph.astream_events(message, thread_id=thread_id):
            pass

    async def check_threads():
        await run_turn("First turn", "conversation-123")
        await run_turn("Second turn", "conversation-123")
        await run_turn("Other chat", "conversation-456")

        first = await graph.application_graph.aget_state(
            {"configurable": {"thread_id": "conversation-123"}}
        )
        second = await graph.application_graph.aget_state(
            {"configurable": {"thread_id": "conversation-456"}}
        )
        return first.values["messages"], second.values["messages"]

    first_messages, second_messages = asyncio.run(check_threads())

    assert [message.content for message in first_messages if message.type == "human"] == [
        "First turn", "Second turn"
    ]
    assert [message.content for message in second_messages if message.type == "human"] == [
        "Other chat"
    ]
    assert model.seen_turns == [
        ["First turn"],
        ["First turn", "Second turn"],
        ["Other chat"],
    ]


def test_graph_loads_summary_and_summarizes_only_older_completed_turns():
    class FakeSummaryRepository:
        def __init__(self):
            self.thread_ids = []
            self.saved = []
            self.snapshot = SummarySnapshot("Stored summary", "earlier-message-id", 1)

        async def latest_active(self, thread_id):
            self.thread_ids.append(thread_id)
            return self.snapshot

        async def save(self, *, thread_id, content, covers_through_message_id, model_name):
            self.saved.append((thread_id, content, covers_through_message_id, model_name))
            self.snapshot = SummarySnapshot(content, covers_through_message_id, self.snapshot.revision + 1)
            return self.snapshot

    class FakeModel:
        tools = []
        model_name = "fake-model"

        def __init__(self):
            self.summary_inputs = []
            self.model_summaries = []

        async def summarize(self, previous_summary, messages):
            self.summary_inputs.append((previous_summary, [message.content for message in messages]))
            return "Extended summary"

        def call_model(self, state):
            self.model_summaries.append(state.get("summary"))
            return {"messages": [AIMessage(content="ok")]}

    repository = FakeSummaryRepository()
    model = FakeModel()
    graph = Graph(
        model,
        checkpointer=InMemorySaver(),
        summary_repository=repository,
        context_window_size=1,
    )

    async def run_turns():
        for message in ("First turn", "Second turn", "Current turn", "Fourth turn"):
            async for _ in graph.astream_events(message, thread_id="conversation-123"):
                pass
        return await graph.application_graph.aget_state(
            {"configurable": {"thread_id": "conversation-123"}}
        )

    state = asyncio.run(run_turns())

    assert repository.thread_ids == ["conversation-123"] * 4
    assert model.summary_inputs == [
        ("Stored summary", ["First turn", "ok"]),
        ("Extended summary", ["Second turn", "ok"]),
    ]
    assert model.model_summaries == ["Stored summary", "Stored summary", "Extended summary", "Extended summary"]
    assert len(repository.saved) == 2
    assert repository.saved[0][0:2] == ("conversation-123", "Extended summary")
    assert repository.saved[0][2] != repository.saved[1][2]
    assert state.values["summary"] == "Extended summary"
