from fastapi import APIRouter, WebSocket


dependencies_router = APIRouter(prefix="/dependencies", tags=["P2P communication"])

"""A python script for the dependencies"""
@app.websocket("/ws")
async def websocket_another_endpoint(websocket: WebSocket):