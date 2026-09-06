from typing import Literal

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel


def route(state: MessagesState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


class Graph(BaseModel):
    def __init__(self, model_name: str, tools: list):
        super().__init__()
        self.model = ChatOpenAI(model=model_name)
        self.tools = tools
        self.bound = self.model.bind_tools(tools)

    def create_graph_agent(self):
        graph = (
            StateGraph(MessagesState)
            .add_node("model", self.call_model)
            .add_node("tools", ToolNode(self.tools))
            .add_edge(START, "model")
            .add_conditional_edges("model", route)
            .add_edge("tools", "model")
            .compile()
        )

        return graph

    def call_model(self, state: MessagesState) -> dict:
        return {"messages": [self.bound.invoke(state["messages"])]}
