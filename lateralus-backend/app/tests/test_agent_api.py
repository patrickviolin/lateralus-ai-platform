from fastapi.testclient import TestClient

from app.main import app


class FakeRunner:
    def __init__(self):
        self.received_messages = []
        self.received_thread_ids = []

    async def execute(self, message: str, *, thread_id: str | None = None):
        self.received_messages.append(message)
        self.received_thread_ids.append(thread_id)
        yield 'event: on_chat_model_end\ndata: {"content": "ok"}\n\n'


class FakeContainer:
    def __init__(self, runner: FakeRunner):
        self.runner = runner


def test_execute_streams_agent_events():
    fake_runner = FakeRunner()
    app.state.container = FakeContainer(fake_runner)

    client = TestClient(app)
    response = client.post("/agent/execute", json={"message": "Weather in Recife"})

    assert response.status_code == 200
    assert fake_runner.received_messages == ["Weather in Recife"]
    assert fake_runner.received_thread_ids == [None]
    assert "text/event-stream" in response.headers["content-type"]
    assert 'event: on_chat_model_end' in response.text
    assert 'data: {"content": "ok"}' in response.text
