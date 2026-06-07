from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api.routes import post_comments, track_comments, like_comments
from src.db.init_collections import init_collections
from src.db.mongo_client import mongodb_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await mongodb_client.connect()
    await init_collections()
    yield
    await mongodb_client.close()


app = FastAPI(
    title="Comment Service",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "tryItOutEnabled": True,
    },
)
app.include_router(post_comments.router)
app.include_router(track_comments.router)
app.include_router(like_comments.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "comment_service"}
