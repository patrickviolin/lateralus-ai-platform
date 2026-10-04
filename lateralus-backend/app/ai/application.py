from dataclasses import dataclass

from app.ai.infra.http_initializer import DefaultAsyncHttpClient
from app.ai.infra.postgres_initializer import PostgresResources
from app.ai.infra.redis_initializer import RedisResources
from app.ai.runtime.runner import Runner
from app.config import Settings


@dataclass
class ApplicationContainer:
    settings: Settings
    runner: Runner
    http_client: DefaultAsyncHttpClient
    redis: RedisResources
    postgres: PostgresResources

    async def close(self) -> None:
        await self.http_client.close()
        await self.redis.close()
        await self.postgres.close()
