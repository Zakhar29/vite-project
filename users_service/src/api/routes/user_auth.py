from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid

from src.db.postgres_engine import get_db, init_db
from src.services.auth_service import AuthService
from src.api.dependencies import get_current_user, get_redis_client
from src.api.schemas import UserCreate, UserLogin, UserResponse, Token, UserList
from src.models.users_models import Users, Followers, Friends

router = APIRouter(
    prefix="/auth",
    tags=["User Authentication"],
)


@router.post("/register", response_model=Token)
async def register(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(db, redis)
    return await auth_service.register(user_data)


@router.post("/login", response_model=Token)
async def login(
        login_data: UserLogin,
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(db, redis)
    return await auth_service.login(login_data)


@router.post("/refresh", response_model=Token)
async def refresh(
        refresh_token: str,
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(db, redis)
    return await auth_service.refresh_tokens(refresh_token)


@router.post("/logout")
async def logout(
        current_user: Users = Depends(get_current_user),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(None, redis)
    await auth_service.logout(str(current_user.id))
    return {"message": "Successfully logged out"}


