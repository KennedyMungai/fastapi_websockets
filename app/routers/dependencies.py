"""A python script for the dependencies"""
from typing import Optional

from fastapi import APIRouter, Cookie, WebSocket, status
from starlette.websockets import WebSocketDisconnect


dependencies_router = APIRouter(
    prefix="/dependencies", tags=["P2P communication"])

"""A python script for the dependencies"""


@dependencies_router.websocket("/ws")
async def websocket_another_endpoint(
    websocket: WebSocket,
    username: str = "Anonymous",
    token: Optional[str] = Cookie(None)
):
    """A websocket endpoint with some dependencies

    Args:
        websocket (WebSocket): A websocket object
    """
    if token != API_TOKEN:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    await websocket.send_text(f"Hello, {username}!")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        await websocket.close()
