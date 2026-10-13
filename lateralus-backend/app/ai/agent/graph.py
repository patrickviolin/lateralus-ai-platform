from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from app.ai.agent.model import Model
from app.ai.infra.postgres.summary_repository import SummaryRepository


class AgentState(MessagesState):
    summary: str
    summary_covers_through_message_id: str | None


def route(state: AgentState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


class Graph:
    def __init__(
        self,
        model: Model,
        checkpointer=None,
        summary_repository: SummaryRepository | None = None,
        context_window_size: int = 10,
    ):
        self.model = model
        self.checkpointer = checkpointer
        self.summary_repository = summary_repository
        self.context_window_size = context_window_size
        self.application_graph = self.create_graph_agent()

    async def load_summary(self, config: RunnableConfig) -> dict:
        if self.summary_repository is None:
            return {}
        thread_id = config.get("configurable", {}).get("thread_id")
        if thread_id is None:
            return {}
        summary = await self.summary_repository.latest_active(str(thread_id))
        return {
            "summary": summary.content if summary else "",
            "summary_covers_through_message_id": summary.covers_through_message_id if summary else None,
        }

    async def summarize(self, state: AgentState, config: RunnableConfig) -> dict:
        messages = state["messages"]
        covered_id = state.get("summary_covers_through_message_id")
        covered_index = next(
            (index for index, message in enumerate(messages) if message.id == covered_id),
            -1,
        ) if covered_id else -1
        unsummarized_messages = messages[covered_index + 1:]
        if count_tokens_approximately(unsummarized_messages) <= self.context_window_size:
            return {}

        # Keep the current message and the most recent completed turn in context.
        past = messages[:-1] if messages and isinstance(messages[-1], HumanMessage) else messages
        turn_starts = [index for index, message in enumerate(past) if isinstance(message, HumanMessage)]
        if len(turn_starts) < 2:
            return {}

        older_completed_turns = past[covered_index + 1:turn_starts[-1]]
        if not older_completed_turns:
            return {}

        summary = await self.model.summarize(state.get("summary", ""), older_completed_turns)
        if self.summary_repository is None:
            return {"summary": summary}

        covered_message_id = older_completed_turns[-1].id
        if covered_message_id is None:
            raise ValueError("Cannot save a summary without a covered message ID")
        thread_id = config.get("configurable", {}).get("thread_id")
        if thread_id is None:
            raise ValueError("Cannot save a summary without a thread ID")
        snapshot = await self.summary_repository.save(
            thread_id=str(thread_id),
            content=summary,
            covers_through_message_id=covered_message_id,
            model_name=self.model.model_name,
        )
        return {
            "summary": snapshot.content,
            "summary_covers_through_message_id": snapshot.covers_through_message_id,
        }

    def create_graph_agent(self) -> CompiledStateGraph:
        compile_options = {}
        if self.checkpointer is not None:
            compile_options["checkpointer"] = self.checkpointer

        graph = (StateGraph(AgentState)
                 .add_node("load_summary", self.load_summary)
                 .add_node("summarize", self.summarize)
                 .add_node("model", self.model.call_model)
                 .add_node("tools", ToolNode(self.model.tools))
                 .add_edge(START, "load_summary")
                 .add_edge("load_summary", "summarize")
                 .add_edge("summarize", "model")
                 .add_conditional_edges("model", route)
                 .add_edge("tools", "model")
                 .compile(**compile_options))

        return graph

    def astream_events(self, message: str, *, version: str = "v2", include_types=None, thread_id: str | None = None):
        options = {"version": version, "include_types": include_types}
        if thread_id is not None:
            options["config"] = {"configurable": {"thread_id": thread_id}}

        return self.application_graph.astream_events({"messages": [{"role": "user", "content": message}]}, **options)
