from app.ai.agent import Agent
from app.api.schemas import ApiRequest
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/agent", tags=["Call agent"])

agent = Agent()


@router.post("/execute", responses={
        200: {"description": "Successful Response"},
        500: {"description": "Internal Server Error"},
    },
)
async def execute_agent(request: ApiRequest) -> StreamingResponse:
    """Call agent. If weather is asked, a tool will be called"""

    try:
        return StreamingResponse(
            agent.execute(request.message),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            })
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error when processing request. Error: {err}",
        )
