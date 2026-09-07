import json
import time

from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given location. Stub implementation."""
    time.sleep(2.2)
    return json.dumps(
        {
            "city": city,
            "temp_c": 22,
            "condition": "parcialmente nublado",
        },
        ensure_ascii=False,
    )
