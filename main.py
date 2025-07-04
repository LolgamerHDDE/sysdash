from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

template = Jinja2Templates(directory="frontend")

@app.get("/")
async def root(requests: Request):
    return {
        "message": "Hello World!",
        "requests": requests
    }

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)