from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
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


def route(state: AgentState) -> Literal["tools", "summarize"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "summarize"


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

    async def load_summary(self, state: AgentState, config: RunnableConfig) -> dict:
        if self.summary_repository is None:
            return {}
        thread_id = config.get("configurable", {}).get("thread_id")
        if thread_id is None:
            return {}
        summary = await self.summary_repository.latest_active(str(thread_id))
        result = {
            "summary": summary.content if summary else "",
            "summary_covers_through_message_id": summary.covers_through_message_id if summary else None,
        }
        if summary is not None:
            # A save can commit before LangGraph checkpoints the removals. Finish that
            # pruning on the next turn, before the model sees the covered messages.
            covered_index = next(
                (index for index, message in enumerate(state["messages"])
                 if message.id == summary.covers_through_message_id),
                -1,
            )
            if covered_index >= 0:
                result["messages"] = [
                    RemoveMessage(id=message.id)
                    for message in state["messages"][:covered_index + 1]
                ]
        return result

    async def summarize(self, state: AgentState, config: RunnableConfig) -> dict:
        messages = state["messages"]
        covered_id = state.get("summary_covers_through_message_id")
        covered_index = next((index for index, message in enumerate(messages) if message.id == covered_id), -1) if covered_id else -1

        unsummarized_messages = messages[covered_index + 1:]
        if count_tokens_approximately(unsummarized_messages) <= self.context_window_size:
            return {}

        # This node runs after the final assistant response, so every turn here is complete.
        turn_starts = [index for index, message in enumerate(unsummarized_messages) if isinstance(message, HumanMessage)]
        if not turn_starts:
            return {}

        # Keep the newest completed turn when there is an older one to summarize.
        # A single long turn must be summarized in full to meet the trigger.
        to_summarize = (unsummarized_messages[:turn_starts[-1]] if len(turn_starts) > 1 else unsummarized_messages)

        summary = await self.model.summarize(state.get("summary", ""), to_summarize)
        if self.summary_repository is None:
            return {"summary": summary}

        if any(message.id is None for message in to_summarize):
            raise ValueError("Cannot save a summary when a covered message has no ID")
        covered_message_id = to_summarize[-1].id
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
            "messages": [RemoveMessage(id=message.id) for message in to_summarize],
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
                 .add_edge("load_summary", "model")
                 .add_conditional_edges("model", route)
                 .add_edge("tools", "model")
                 .add_edge("summarize", END)
                 .compile(**compile_options))

        return graph

    def astream_events(self, message: str, *, version: str = "v2", include_types=None, thread_id: str | None = None):
        options = {"version": version, "include_types": include_types}
        if thread_id is not None:
            options["config"] = {"configurable": {"thread_id": thread_id}}

        return self.application_graph.astream_events({"messages": [{"role": "user", "content": message}]}, **options)
