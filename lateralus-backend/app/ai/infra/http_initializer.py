from dataclasses import dataclass, field
from typing import Any


@dataclass
class DefaultAsyncHttpClient:
    _client: Any | None = field(default=None, init=False)

    @property
    def client(self) -> Any:
        if self._client is None:
            import httpx

            self._client = httpx.AsyncClient(http2=True)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()


async def create_http_client() -> DefaultAsyncHttpClient:
    return DefaultAsyncHttpClient()
