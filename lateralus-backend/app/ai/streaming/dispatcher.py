from collections.abc import Mapping
from typing import Any

from app.ai.streaming.handler import StreamHandler

INCLUDE_TYPES = ["chat_model", "tool"]

EVENTS = (
    "on_chat_model_start",
    "on_chat_model_stream",
    "on_chat_model_end",
    "on_tool_start",
    "on_tool_end",
)

class UnknownStreamType(RuntimeError):
    def __init__(self, kind: str) -> None:
        super().__init__(f"unknown stream type: {kind}")
        self.kind = kind

class StreamDispatcher:
    def __init__(self, handlers: Mapping[str, StreamHandler]) -> None:
        self._handlers = dict(handlers)

    @classmethod
    def default(cls) -> StreamDispatcher:
        return cls({name: StreamHandler(name) for name in EVENTS})

    @property
    def include_types(self) -> list[str]:
        return list(INCLUDE_TYPES)

    def dispatch(self, event: Mapping[str, Any]) -> str:
        kind = event["event"]
        handler = self._handlers.get(kind)
        if handler is None:
            raise UnknownStreamType(kind)
        return handler.handle(event)