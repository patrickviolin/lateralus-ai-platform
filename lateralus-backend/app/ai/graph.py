from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from app.ai.model import Model


def route(state: MessagesState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


class Graph:
    def __init__(self, model: Model, checkpointer=None):
        self.model = model
        self.checkpointer = checkpointer
        self.application_graph = self.create_graph_agent()

    def create_graph_agent(self) -> CompiledStateGraph:
        compile_options = {}
        if self.checkpointer is not None:
            compile_options["checkpointer"] = self.checkpointer

        graph = (StateGraph(MessagesState).add_node("model", self.model.call_model)
                 .add_node("tools", ToolNode(self.model.tools))
                 .add_edge(START, "model")
                 .add_conditional_edges("model", route)
                 .add_edge("tools", "model")
                 .compile(**compile_options))

        return graph

    def astream_events(self, message: str, *, version: str = "v2", include_types=None, thread_id: str | None = None, ):
        options = {"version": version, "include_types": include_types, }
        if thread_id is not None:
            options["config"] = {"configurable": {"thread_id": thread_id}}

        return self.application_graph.astream_events({"messages": [{"role": "user", "content": message}]}, **options, )
