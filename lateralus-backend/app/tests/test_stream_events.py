import json

import pytest

from app.ai.sse_event import SseEvent
from app.ai.streaming.dispatcher import StreamDispatcher, UnknownStreamType
from app.ai.tools.schemas import GetWeatherResponse


def test_sse_event_serializes_langchain_event():
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

    result = SseEvent("on_tool_end", event).encode()

    assert result.startswith("event: on_tool_end\n")
    assert result.endswith("\n\n")

    payload = result.split("data: ", maxsplit=1)[1]
    serialized_event = json.loads(payload)
    assert serialized_event["event"] == "on_tool_end"
    assert serialized_event["run_id"] == "run-123"
    output = serialized_event["data"]["output"]
    assert output["lc"] == 1
    assert output["type"] == "not_implemented"
    assert output["id"] == ["app", "ai", "tools", "schemas", "GetWeatherResponse"]
    assert "Rio de Janeiro" in output["repr"]


def test_stream_dispatcher_dispatches_known_events():
    dispatcher = StreamDispatcher.default()
    event = {
        "event": "on_chat_model_end",
        "run_id": "run-123",
        "data": {"content": "ok"},
    }

    result = dispatcher.dispatch(event)

    assert result.startswith("event: on_chat_model_end\n")
    payload = result.split("data: ", maxsplit=1)[1]
    serialized_event = json.loads(payload)
    assert serialized_event == event


def test_stream_dispatcher_rejects_unknown_events():
    dispatcher = StreamDispatcher.default()

    with pytest.raises(UnknownStreamType) as exc_info:
        dispatcher.dispatch({"event": "on_chain_stream"})

    assert exc_info.value.kind == "on_chain_stream"
