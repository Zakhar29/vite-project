import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

#from src.api.routes import albums, auth, feed, posts
from src.kafka.consumer import event_consumer
from src.kafka.producer import event_producer

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await event_producer.start()
    await event_consumer.start()
    consumer_task = asyncio.create_task(event_consumer.run())
    yield
    consumer_task.cancel()
    await event_consumer.stop()
    await event_producer.stop()


app = FastAPI(title="Gateway Service (BFF)", lifespan=lifespan)


if STATIC_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(STATIC_DIR), html=True), name="ui")


@app.get("/")
async def root():
    return RedirectResponse(url="/ui/")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gateway_service"}
