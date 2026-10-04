from fastapi import FastAPI

import app.config
from app.ai.lifespan import application_lifespan
from app.api.routers import agent_router, health_router

app = FastAPI(
    title="Lateralus API",
    description="An API for interacting with Lateralus agents",
    version="1.0.0",
    lifespan=application_lifespan,
)

app.include_router(agent_router.router)
app.include_router(health_router.router)
