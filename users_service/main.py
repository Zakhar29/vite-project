from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid

from src.db.postgres_engine import get_db, init_db
from src.services.auth_service import AuthService
from src.api.dependencies import get_current_user, get_redis_client
from src.api.schemas import UserCreate, UserLogin, UserResponse, Token, UserList
from src.models.users_models import Users, Followers, Friends
from src.api.routes import user_auth, user_info, user_settings, user_follows

app = FastAPI(title="User Service API")
app.include_router(user_auth.router)
app.include_router(user_info.router)
app.include_router(user_settings.router)
app.include_router(user_follows.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


# Альтернативно, можно просто показать информацию
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "User Service"}


@app.on_event("startup")
async def startup():
    await init_db()
