from app.api.schemas import ApiRequest
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/agent", tags=["Call agent"])


@router.post(
    "/execute",
    responses={
        200: {"description": "Successful Response"},
        500: {"description": "Internal Server Error"},
    },
)
async def execute_agent(request: Request, payload: ApiRequest) -> StreamingResponse:
    """Call agent. If weather is asked, a tool will be called"""

    try:
        runner = request.app.state.container.runner
        return StreamingResponse(
            runner.execute(payload.message, thread_id=payload.thread_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error when processing request. Error: {err}",
        )
