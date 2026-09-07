import json

from app.ai.tools import weather as weather_module


def test_get_weather_returns_serialized_weather(monkeypatch):
    monkeypatch.setattr(weather_module.time, "sleep", lambda _: None)

    result = weather_module.get_weather.invoke({"city": "São Paulo"})

    assert json.loads(result) == {
        "city": "São Paulo",
        "temp_c": 22,
        "condition": "parcialmente nublado",
    }
