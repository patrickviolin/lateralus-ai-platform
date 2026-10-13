from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.ai.agent.prompts import SYSTEM_PROMPT

SUMMARY_PROMPT = (
    "Summarize the completed conversation turns for future turns in this same chat. "
    "Preserve the user's constraints, preferences, unresolved questions, and important tool results. "
    "Do not invent facts. Keep the summary concise."
)


class Model:
    def __init__(self, tools: list, *, model: str = "gpt-4o-mini", timeout: float = 5.0, max_retries: int = 0):
        self.model_name = model
        self.foundation_model = ChatOpenAI(model=model, timeout=timeout, max_retries=max_retries)
        self.tools = tools
        self.bound = self.foundation_model.bind_tools(tools)

    async def summarize(self, previous_summary: str, messages: list[BaseMessage]) -> str:
        instruction = (
            f"Previous summary:\n{previous_summary}\n\nExtend it with the conversation above."
            if previous_summary
            else "Summarize the conversation above."
        )
        response = await self.foundation_model.ainvoke(
            [SystemMessage(content=SUMMARY_PROMPT), *messages, HumanMessage(content=instruction)],
            config={"tags": ["memory_summary"]},
        )
        return response.content if isinstance(response.content, str) else str(response.content)

    async def call_model(self, state: dict) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        return {"messages": [await self.bound.ainvoke(messages)]}
