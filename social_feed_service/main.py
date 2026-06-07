from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api.routes import posts
from src.db.init_collections import init_collections
from src.db.mongo_client import mongodb_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await mongodb_client.connect()
    await init_collections()
    yield
    await mongodb_client.close()


app = FastAPI(
    title="Social Feed Service",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
    },
)
app.include_router(posts.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "social_feed_service"}
