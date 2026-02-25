from fastapi import APIRouter
from tabby.common.api.server_setting import ServerSetting

router = APIRouter(prefix="/v1beta", tags=["v1beta"])

@router.get(
    "/server_setting",
    response_model=ServerSetting,
    summary="Get server settings",
    operation_id="config"
)
async def get_server_setting() -> ServerSetting:
    return ServerSetting(
        model="tabby-python-backend",      # Add this
        chat_model="tabby-python-backend", # Add this
        disable_client_side_telemetry=False
    )