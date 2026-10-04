from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from app.ai.prompts import SYSTEM_PROMPT


class Model:
    def __init__(self, tools: list, *, model: str = "gpt-4o-mini", timeout: float = 3.0, max_retries: int = 0):
        self.foundation_model = ChatOpenAI(model=model, timeout=timeout, max_retries=max_retries)
        self.tools = tools
        self.bound = self.foundation_model.bind_tools(self.tools)

    def call_model(self, state: MessagesState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        return {"messages": [self.bound.invoke(messages)]}
