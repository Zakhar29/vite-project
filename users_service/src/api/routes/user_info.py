from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid

from src.db.postgres_engine import get_db, init_db
from src.services.auth_service import AuthService
from src.api.dependencies import get_current_user, get_redis_client
from src.api.schemas import UserCreate, UserLogin, UserResponse, Token, UserList
from src.models.users_models import Users, Followers, Friends, UserStatuses

router = APIRouter(
    prefix="/users",
    tags=["User Information"],
)


# Пользователи
@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Users = Depends(get_current_user)
):
    return current_user


@router.get("/get_user_info/{user_id}")
async def get_user_info(
    user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_name": user.username,
        "user_nickname": user.nickname,
        "user_avatar": user.avatar_url,
        "user_bio": user.bio,
        "user_follower_quantity": user.follower_quantity,
        "user_following_quantity": user.following_quantity,
        "user_friends_quantity": user.friends_quantity,
        "user_listening_quantity": user.listening_quantity,
        "user_month_listening_quantity": user.month_listening_quantity
    }


@router.get("/get_user/{user_id}")
async def get_user(
    user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_nickname": user.nickname,
        "user_avatar": user.avatar_url,
    }


@router.get("/get_user_status/{user_id}")
async def get_user_status(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStatuses).where(UserStatuses.id == user_id))
    user_status = result.scalar_one_or_none()
    if not user_status:
        raise HTTPException(status_code=404, detail="User status not found")
    return user_status.title


@router.get("/followers/{user_id}")
async def get_followers(
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Users).join(Followers, Followers.follower_id == Users.id)
        .where(Followers.following_id == user_id)
        .offset(skip).limit(limit)
    )
    followers = result.scalars().all()
    return followers


@router.get("/following/{user_id}")
async def get_following(
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Users).join(Followers, Followers.following_id == Users.id)
        .where(Followers.follower_id == user_id)
        .offset(skip).limit(limit)
    )
    following = result.scalars().all()
    return following


@router.get("/friends/{user_id}")
async def get_friends(
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = Depends(get_db)
):
    friends_result = await db.execute(
        select(Users)
        .where(
            Users.id.in_(
                select(Friends.friend2).where(Friends.friend1 == user_id)
                .union(
                    select(Friends.friend1).where(Friends.friend2 == user_id)
                )
            )
        )
        .offset(skip).limit(limit)
    )
    friends_list = friends_result.scalars().all()
    
    return {
        "friends": [
            {
                "friend_id": str(f.id),
                "nickname": f.nickname,
                "avatar_url": f.avatar_url
            } for f in friends_list
        ]
    }
