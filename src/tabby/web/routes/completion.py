from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from tabby.common.api.completion import CompletionRequest, CompletionResponse

router = APIRouter()

@router.post("/completions") # Removed response_model because it can return JSON OR a Stream
async def completions(
    request: Request,
    completion_request: CompletionRequest,
    user_agent: Optional[str] = Header(None)
):
    service = getattr(request.app.state, "completion_service", None)
    
    if not service:
        raise HTTPException(
            status_code=500, 
            detail="Completion service not initialized."
        )

    try:
        # Check if the user wants a stream
        if completion_request.stream:
            # Returns an async generator from your service
            gen = service.generate_stream(completion_request, user_agent=user_agent)
            
            # Use Server-Sent Events (SSE) format
            async def event_generator():
                async for chunk in gen:
                    # vLLM/Tabby usually expects chunks wrapped in JSON strings
                    # Format: data: {"choices": [{"text": "..."}]}
                    yield f"data: {json.dumps(chunk.dict())}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")
        
        else:
            # Standard non-streaming logic
            response = await service.generate(completion_request, user_agent=user_agent)
            return response
            
    except Exception as e:
        print(f"Error during completion: {e}")
        raise HTTPException(status_code=400, detail=str(e))