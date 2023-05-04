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
