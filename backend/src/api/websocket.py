import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.security import decode_token

logger = logging.getLogger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws/alerts")
async def alert_stream(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time alert streaming.

    Authenticate via query param: ?token=<jwt>
    Server pushes:
      {"type": "alert", "data": {...}}
      {"type": "system_update"}
      {"type": "data_change", "queryKeys": [["rooms"], ["residents"]]}
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        decode_token(token)
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    manager = websocket.app.state.ws_manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive pings
    except WebSocketDisconnect:
        manager.disconnect(websocket)
