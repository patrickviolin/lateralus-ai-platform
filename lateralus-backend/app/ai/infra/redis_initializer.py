from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Any

from app.config import Settings


@dataclass
class RedisResources:
    url: str
    checkpointer: Any | None = None
    _context: AbstractAsyncContextManager | None = None

    async def close(self) -> None:
        if self._context is not None:
            await self._context.__aexit__(None, None, None)


async def create_redis_resources(settings: Settings) -> RedisResources:
    if not settings.redis_checkpoint_enabled:
        return RedisResources(url=settings.redis_url)

    from langgraph.checkpoint.redis.aio import AsyncRedisSaver

    context = AsyncRedisSaver.from_conn_string(settings.redis_url, ttl={"default_ttl": settings.redis_ttl_minutes})
    checkpointer = await context.__aenter__()

    return RedisResources(
        url=settings.redis_url,
        checkpointer=checkpointer,
        _context=context,
    )
