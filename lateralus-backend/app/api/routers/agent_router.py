from fastapi import APIRouter, HTTPException
from fastapi.sse import EventSourceResponse

from app.ai.agent import Agent
from app.api.schemas import ApiRequest

router = APIRouter(
    prefix="/agent",
    tags=["Call agent"]
)


@router.post("/execute",
             responses={200: {"description": "Successful Response"},
                        500: {"description": "Internal Server Error"}})
async def call_agent(request: ApiRequest) -> EventSourceResponse:
    """Call agent. If weather is asked, a tool will be called"""

    try:
        agent = Agent()
        return EventSourceResponse(agent.use_agent(request.message))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f'Internal error when processing request. Error: {err}')
