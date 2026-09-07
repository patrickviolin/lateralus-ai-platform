from app.ai.prompts import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from app.ai.tools.schemas import GetWeatherResponse


class Model:
    def __init__(self, tools: list):
        self.foundation_model = ChatOpenAI(model='gpt-4o-mini', timeout=3.0, max_retries=0)
        self.tools = tools
        self.bound = self.foundation_model.bind_tools(self.tools)

    def call_model(self, state: MessagesState) -> dict:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"]
        ]
        return {"messages": [self.bound.invoke(messages)]}
