from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid
from passlib.context import CryptContext

from src.db.postgres_engine import get_db, init_db
from src.services.auth_service import AuthService
from src.api.dependencies import get_current_user, get_redis_client
from src.api.schemas import UserCreate, UserLogin, UserResponse, Token, UserList
from src.models.users_models import Users, Followers, Friends

router = APIRouter(
    prefix="/settings",
    tags=["User Settings"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/avatar", status_code=201)
async def avatar_upload(
        avatar_url: str,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    await db.execute(
        update(Users)
        .where(Users.id == current_user.id)
        .values(avatar_url=avatar_url)
    )
    await db.commit()
    return {"message": "Avatar uploaded successfully"}


@router.post("/bio", status_code=201)
async def bio_upload(
        bio: str,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    await db.execute(
        update(Users)
        .where(Users.id == current_user.id)
        .values(bio=bio)
    )
    await db.commit()
    return {"message": "Bio uploaded successfully"}


@router.post("/rename_nickname", status_code=201)
async def rename_nickname(
        nickname: str,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    await db.execute(
        update(Users)
        .where(Users.id == current_user.id)
        .values(nickname=nickname)
    )
    await db.commit()
    return {"message": "Nickname renamed successfully"}


@router.post("/rename_username", status_code=201)
async def rename_username(
        username: str,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    # Проверка на уникальность
    existing = await db.execute(select(Users).where(Users.username == username))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Username already taken")
    
    await db.execute(
        update(Users)
        .where(Users.id == current_user.id)
        .values(username=username)
    )
    await db.commit()
    return {"message": "Username renamed successfully"}


@router.post("/change_password", status_code=201)
async def change_password(
        password: str,
        new_password: str,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if not pwd_context.verify(password, current_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    hashed_new = pwd_context.hash(new_password)
    
    await db.execute(
        update(Users)
        .where(Users.id == current_user.id)
        .values(password=hashed_new)
    )
    await db.commit()
    return {"message": "Password changed successfully"}
