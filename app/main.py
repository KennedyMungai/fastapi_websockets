"""This is the entrypoint to the project"""
import asyncio
from datetime import datetime

from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from app.routers.dependencies import dependencies_router

app = FastAPI()


broadcast = Broadcast("redis://localhost:6379")
CHANNEL = "CHAT"


class MessageEvent(BaseModel):
    """This is the message event class"""
    username: str
    message: str


async def receive_message(websocket: WebSocket, username: str):
    """The receive message function

    Args:
        websocket (WebSocket): The websocket object
        username (str): The username
    """
    async with broadcast.subscribe(channel=CHANNEL) as subscriber:
        async for event in subscriber:
            message_event = MessageEvent.parse_raw(event.message)

            # Discard the users own message
            if message_event.username != username:
                await websocket.send_json(message_event.dict())


@app.get(
    "/",
    name="home",
    description="This is the root endpoint for the application",
    tags=["Home"]
)
async def home() -> dict[str, str]:
    """This is the home endpoint"""
    return {"message": "Hello World"}

app.include_router(dependencies_router)


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
    """The websocket endpoint

    Args:
        websocket (WebSocket): A websocket object
    """
    await websocket.accept()

    try:
        while True:
            echo_message_task = asyncio.create_task(echo_message(websocket))
            send_time_task = asyncio.create_task(send_time(websocket))

            done, pending = await asyncio.wait({echo_message_task, send_time_task}, return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                task.cancel()
            for task in done():
                task.result()
    except WebSocketDisconnect():
        await websocket.close()
