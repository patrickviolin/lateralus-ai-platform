from fastapi.testclient import TestClient

from app.api.routers import agent_router
from app.main import app


class FakeAgent:
    def __init__(self):
        self.received_messages = []

    async def use_agent(self, message: str):
        self.received_messages.append(message)
        yield 'event: on_chat_model_end\ndata: {"content": "ok"}\n\n'


def test_execute_streams_agent_events(monkeypatch):
    fake_agent = FakeAgent()
    monkeypatch.setattr(agent_router, "agent", fake_agent)

    client = TestClient(app)
    response = client.post("/agent/execute", json={"message": "Weather in Recife"})

    assert response.status_code == 200
    assert fake_agent.received_messages == ["Weather in Recife"]
    assert 'event: on_chat_model_end' in response.text
    assert 'data: {"content": "ok"}' in response.text
