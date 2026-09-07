from langchain_core.messages import AIMessage
from langgraph.constants import END

from app.ai.graph import route


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


def test_route_ends_when_no_tool_calls_exist():
    state = {"messages": [AIMessage(content="The weather is available.")]}

    assert route(state) == END
