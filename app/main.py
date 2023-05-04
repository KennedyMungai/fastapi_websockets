"""This is the entrypoint to the project"""
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect


app = FastAPI()


@app.get(
    "/",
    name="home",
    description="This is the root endpoint for the application",
    tags=["Home"]
)
async def home() -> dict[str, str]:
    """This is the home endpoint"""
    return {"message": "Hello World"}


async def echo_message(websocket: WebSocket):
    """This os a function that shows the message

    Args:
        websocket (WebSocket): The websocket object
    """
    data = await websocket.receive_text()
    await websocket.send_text(f"Message text was: {data}")


async def send_time(websocket: WebSocket):
    """Defined a function that will show the send time of messages

    Args:
        websocket (WebSocket): The websocket object
    """
    await asyncio.sleep(10)
    await websocket.send_text(f"It is: {datetime.utcnow().isoformat()}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """A simple websocket endpoint

    Args:
        websocket (WebSocket): The websocket object
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        await websocket.close()
