import asyncio

from langchain_core.messages import AIMessage, HumanMessage

from app.ai.agent.model import Model


def test_model_injects_loaded_summary_into_system_prompt():
    class FakeBoundModel:
        def __init__(self):
            self.messages = None

        async def ainvoke(self, messages):
            self.messages = messages
            return AIMessage(content="answer")

    bound = FakeBoundModel()
    model = Model.__new__(Model)
    model.bound = bound
    user_message = HumanMessage(content="What did I say?")

    result = asyncio.run(model.call_model({
        "summary": "The user prefers answers in Portuguese.",
        "messages": [user_message],
    }))

    assert "The user prefers answers in Portuguese." in bound.messages[0].content
    assert bound.messages[1] is user_message
    assert result["messages"][0].content == "answer"
