from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.ai.lifespan.boot.container_builder import build_container


@asynccontextmanager
async def application_lifespan(app: FastAPI) -> AsyncIterator[None]:
    container = await build_container()
    app.state.container = container
    try:
        yield
    finally:
        await container.close()
