import random

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from data import artists

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def index():
    return "\n".join(random.sample(artists, k=5))


@app.get("/all", response_class=PlainTextResponse)
async def get_all():
    return "\n".join(artists)
