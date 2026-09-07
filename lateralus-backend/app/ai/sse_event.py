from dataclasses import dataclass
from typing import Any

from langchain_core.load.dump import dumps


@dataclass(frozen=True)
class SseEvent:
    """Represents a Server-Sent Event (SSE) with an event type and associated data."""
    event: str
    data: Any

    def encode(self) -> str:
        """Encodes the SSE event into a string format suitable for transmission."""
        return f"event: {self.event}\ndata: {dumps(self.data, ensure_ascii=False)}\n\n"