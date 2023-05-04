"""This is the entrypoint to the project"""
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