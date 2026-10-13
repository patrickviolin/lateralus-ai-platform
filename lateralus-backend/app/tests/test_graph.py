import asyncio

import pytest
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, ToolMessage
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


def test_route_summarizes_after_final_answer():
    state = {"messages": [AIMessage(content="The weather is available.")]}

    assert route(state) == "summarize"


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
    graph = Graph(model, checkpointer=InMemorySaver(), context_window_size=10_000)

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


def test_long_first_turn_is_saved_and_loaded_for_next_turn():
    class FakeSummaryRepository:
        def __init__(self):
            self.thread_ids = []
            self.saved = []
            self.snapshot = None

        async def latest_active(self, thread_id):
            self.thread_ids.append(thread_id)
            return self.snapshot

        async def save(self, *, thread_id, content, covers_through_message_id, model_name):
            self.saved.append((thread_id, content, covers_through_message_id, model_name))
            self.snapshot = SummarySnapshot(content, covers_through_message_id, 1)
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
        context_window_size=25,
    )

    long_message = "Remember this detail about our conversation. " * 30

    async def run_turns():
        for message in (long_message, "What did I say?"):
            async for _ in graph.astream_events(message, thread_id="conversation-123"):
                pass
        return await graph.application_graph.aget_state(
            {"configurable": {"thread_id": "conversation-123"}}
        )

    state = asyncio.run(run_turns())

    assert repository.thread_ids == ["conversation-123"] * 2
    assert model.summary_inputs == [
        ("", [long_message, "ok"]),
    ]
    assert model.model_summaries == ["", "Extended summary"]
    assert len(repository.saved) == 1
    assert repository.saved[0][0:2] == ("conversation-123", "Extended summary")
    assert state.values["summary"] == "Extended summary"
    assert [message.content for message in state.values["messages"]] == ["What did I say?", "ok"]


def test_completed_turn_summarization_reserves_newest_turn():
    class FakeModel:
        tools = []

        def __init__(self):
            self.received = []

        async def summarize(self, previous_summary, messages):
            self.received = [message.content for message in messages]
            return "Summary of first turn"

        def call_model(self, state):
            return {"messages": [AIMessage(content="ok")]}

    model = FakeModel()
    graph = Graph(model, context_window_size=1)
    state = {
        "messages": [
            HumanMessage(content="First", id="h1"),
            AIMessage(content="Answer one", id="a1"),
            HumanMessage(content="Second", id="h2"),
            AIMessage(content="Answer two", id="a2"),
        ],
    }

    result = asyncio.run(graph.summarize(state, {"configurable": {"thread_id": "conversation-123"}}))

    assert model.received == ["First", "Answer one"]
    assert result == {"summary": "Summary of first turn"}


def test_summarize_removes_complete_older_turn_after_save():
    class FakeRepository:
        async def save(self, *, thread_id, content, covers_through_message_id, model_name):
            assert (thread_id, content, covers_through_message_id) == (
                "conversation-123", "Saved summary", "a1"
            )
            return SummarySnapshot(content, covers_through_message_id, 1)

    class FakeModel:
        tools = []
        model_name = "fake-model"

        async def call_model(self, state):
            return {"messages": [AIMessage(content="ok")]}

        async def summarize(self, previous_summary, messages):
            assert [message.id for message in messages] == ["h1", "call", "tool", "a1"]
            return "Saved summary"

    graph = Graph(FakeModel(), summary_repository=FakeRepository(), context_window_size=1)
    state = {
        "messages": [
            HumanMessage(content="First", id="h1"),
            AIMessage(content="", id="call", tool_calls=[{"name": "search", "args": {}, "id": "tool-call"}]),
            ToolMessage(content="result", tool_call_id="tool-call", id="tool"),
            AIMessage(content="Answer one", id="a1"),
            HumanMessage(content="Second", id="h2"),
            AIMessage(content="Answer two", id="a2"),
        ],
    }

    result = asyncio.run(graph.summarize(state, {"configurable": {"thread_id": "conversation-123"}}))

    assert [message.id for message in result["messages"]] == ["h1", "call", "tool", "a1"]
    assert all(isinstance(message, RemoveMessage) for message in result["messages"])
    assert result["summary_covers_through_message_id"] == "a1"


def test_summarize_keeps_messages_when_save_fails():
    class FailingRepository:
        async def save(self, **kwargs):
            raise RuntimeError("database unavailable")

    class FakeModel:
        tools = []
        model_name = "fake-model"

        async def call_model(self, state):
            return {"messages": [AIMessage(content="ok")]}

        async def summarize(self, previous_summary, messages):
            return "Unsaved summary"

    graph = Graph(FakeModel(), summary_repository=FailingRepository(), context_window_size=1)
    messages = [HumanMessage(content="First", id="h1"), AIMessage(content="Answer", id="a1")]

    with pytest.raises(RuntimeError, match="database unavailable"):
        asyncio.run(graph.summarize({"messages": messages}, {"configurable": {"thread_id": "conversation-123"}}))
    assert [message.id for message in messages] == ["h1", "a1"]


def test_load_summary_prunes_covered_messages_after_interrupted_checkpoint():
    class FakeRepository:
        async def latest_active(self, thread_id):
            return SummarySnapshot("Saved summary", "a1", 1)

    class FakeModel:
        tools = []

        async def call_model(self, state):
            return {"messages": [AIMessage(content="ok")]}

    graph = Graph(FakeModel(), summary_repository=FakeRepository())
    state = {
        "messages": [
            HumanMessage(content="First", id="h1"),
            AIMessage(content="Answer one", id="a1"),
            HumanMessage(content="Second", id="h2"),
        ],
    }

    result = asyncio.run(graph.load_summary(state, {"configurable": {"thread_id": "conversation-123"}}))

    assert result["summary"] == "Saved summary"
    assert [message.id for message in result["messages"]] == ["h1", "a1"]
    assert all(isinstance(message, RemoveMessage) for message in result["messages"])
