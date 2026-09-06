from app.ai.prompts import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState


class Model:
    def __init__(self, tools: list):
        self.model = ChatOpenAI(model='gpt-4o-mini')
        self.tools = tools
        self.bound = self.model.bind_tools(self.tools)

    def call_model(self, state: MessagesState) -> dict:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"]
        ]
        return {"messages": [self.bound.invoke(messages)]}
