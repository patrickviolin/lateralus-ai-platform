import json

from langchain_core.runnables.schema import StreamEvent
from pydantic import BaseModel


def format_event_to_sse(event: StreamEvent) -> str:
    """Formats a StreamEvent to a Server-Sent Event (SSE) string."""
    event_type = event["event"]
    data = json.dumps(event, default=model_dump_if_base_model)

    sse_message = f"event: {event_type}\ndata: {data}\n\n"
    return sse_message


def model_dump_if_base_model(content):
    if isinstance(content, BaseModel):
        return content.model_dump(mode="json")
    else:
        raise TypeError(f"Object of type {type(content).__name__} is not JSON serializable")
