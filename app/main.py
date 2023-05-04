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


async def send_message(websocket: WebSocket, username: str):
    """Defined the send message asynchronous function

    Args:
        websocket (WebSocket): The websocket object
        username (str): The username of the sender
    """
    data = await websocket.receive_text()
    event = MessageEvent(username=username, message=data)
    await broadcast.publish(channel=CHANNEL, message=event.json())


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
async def websocket_endpoint(
    websocket: WebSocket,
    username: str = "Anonymous"
) -> None:
    """The websocket endpoint

    Args:
        websocket (WebSocket): A websocket object
    """
    await websocket.accept()

    try:
        while True:
            receive_message_task = asyncio.create_task(
                receive_message(websocket, username))

            send_message_task = asyncio.create_task(
                send_message(websocket, username))

            done, pending = await asyncio.wait(
                {receive_message_task, send_message_task},
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()
            for task in done():
                task.result()
    except WebSocketDisconnect():
        await websocket.close()


@app.on_event("startup")
async def startup():
    """Runs on startup
    """
    await broadcast.connect()


@app.on_event("shutdown")
async def shutdown():
    """Runs on app shutdown
    """
    await broadcast.disconnect()
