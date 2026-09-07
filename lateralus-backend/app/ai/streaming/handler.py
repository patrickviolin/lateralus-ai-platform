from app.ai.sse_event import SseEvent


class StreamHandler:
    def __init__(self, name: str) -> None:
        self.name = name

    def handle(self, event: dict) -> str:
        return SseEvent(self.name, event).encode()
