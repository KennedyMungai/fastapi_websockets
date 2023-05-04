"""This is the entrypoint to the project"""
from fastapi import FastAPI


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
