from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.tools import BaseTool

from app.ai.agent.tools.weather import get_weather


ToolBuilder = Callable[[], BaseTool]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    builder: ToolBuilder

    def create(self) -> BaseTool:
        return self.builder()


@dataclass
class ToolFactory:
    definitions: list[ToolDefinition] = field(default_factory=list)

    def register(self, name: str, builder: ToolBuilder) -> None:
        self.definitions.append(ToolDefinition(name=name, builder=builder))

    def create_tools(self, names: Sequence[str] | None = None) -> list[Any]:
        selected = set(names) if names is not None else None
        return [
            definition.create()
            for definition in self.definitions
            if selected is None or definition.name in selected
        ]


def default_tool_factory() -> ToolFactory:
    factory = ToolFactory()
    factory.register("weather", lambda: get_weather)
    return factory
