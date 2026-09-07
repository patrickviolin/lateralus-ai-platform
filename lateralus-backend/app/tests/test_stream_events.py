import json

from app.ai.events import format_event_to_sse
from app.ai.tools.schemas import GetWeatherResponse


def test_format_event_to_sse_serializes_langchain_event():
    event = {
        "event": "on_tool_end",
        "run_id": "run-123",
        "data": {
            "output": GetWeatherResponse(
                city="Rio de Janeiro",
                temp_c=22,
                condition="parcialmente nublado",
                summary="Está parcialmente nublado no Rio de Janeiro.",
            )
        },
    }

    result = format_event_to_sse(event)

    assert result.startswith("event: on_tool_end\n")
    assert result.endswith("\n\n")

    payload = result.split("data: ", maxsplit=1)[1]
    serialized_event = json.loads(payload)
    assert serialized_event["event"] == "on_tool_end"
    assert serialized_event["run_id"] == "run-123"
    assert serialized_event["data"]["output"] == {
        "city": "Rio de Janeiro",
        "temp_c": 22,
        "condition": "parcialmente nublado",
        "summary": "Está parcialmente nublado no Rio de Janeiro.",
    }
