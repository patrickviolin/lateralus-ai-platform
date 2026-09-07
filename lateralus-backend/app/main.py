from fastapi import FastAPI

import app.config
from app.api.routers import agent_router

app = FastAPI(
    title="Lateralus API",
    description="An API for interacting with Lateralus agents",
    version="1.0.0",
)

app.include_router(agent_router.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "UP"}
