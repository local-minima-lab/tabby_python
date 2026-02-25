from typing import Optional
from fastapi import APIRouter, Query, status, Depends, Response, Request
from tabby.common.api.event import (
    LogEventRequest, 
    ViewEvent, 
    SelectEvent, 
    DismissEvent,
    SelectKind,
    EventLogger,
    NoOpLogger
)

router = APIRouter(prefix="/v1", tags=["v1"])

# --- DEPENDENCIES ---

async def get_event_logger(request: Request) -> EventLogger:
    """
    Dependency to get the event logger service from app state.
    Defaults to NoOpLogger if not initialized (useful for testing).
    """
    return getattr(request.app.state, "event_logger", NoOpLogger())


async def get_current_user() -> Optional[str]:
    """
    Extract user from headers/token.
    TODO: Implement based on your auth system.
    """
    return None


# --- ROUTES ---

@router.post(
    "/events",
    status_code=status.HTTP_200_OK,
    summary="Log completion events",
    operation_id="event",
    responses={
        200: {"description": "Success"},
        400: {"description": "Bad Request"}
    }
)
async def log_event(
    request: LogEventRequest,
    response: Response,
    select_kind: Optional[str] = Query(None),
    user: Optional[str] = Depends(get_current_user),
    logger: EventLogger = Depends(get_event_logger),
):
    """
    Log completion-related events (view, select, dismiss).
    """
    if request.event_type == "view":
        event = ViewEvent(
            completion_id=request.completion_id,
            choice_index=request.choice_index,
            view_id=request.view_id,
        )
        logger.log(user, event)
        return {"status": "ok"}
    
    elif request.event_type == "select":
        is_line = select_kind == "line" if select_kind else False
        event = SelectEvent(
            completion_id=request.completion_id,
            choice_index=request.choice_index,
            kind=SelectKind.LINE if is_line else None,
            view_id=request.view_id,
            elapsed=request.elapsed,
        )
        logger.log(user, event)
        return {"status": "ok"}
    
    elif request.event_type == "dismiss":
        event = DismissEvent(
            completion_id=request.completion_id,
            choice_index=request.choice_index,
            view_id=request.view_id,
            elapsed=request.elapsed,
        )
        logger.log(user, event)
        return {"status": "ok"}
    
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Invalid event type"}