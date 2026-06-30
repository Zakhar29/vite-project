from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, desc, case
from typing import Optional, List
import uuid

from src.db.postgres_engine import get_db
from src.api.dependencies import get_current_user, get_optional_current_user
from src.api.schemas import UserResponse
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
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_optional_current_user)
):
    """Получение информации о пользователе с статусом подписки."""
    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Статус подписки
    follow_status = "none"  # none, following, friend
    
    if current_user and current_user.id != user_id:
        # Проверяем, подписан ли текущий пользователь
        follow = await db.scalar(
            select(Followers).where(
                Followers.follower_id == current_user.id,
                Followers.following_id == user_id
            )
        )
        
        if follow:
            # Проверяем, есть ли взаимная подписка (друзья)
            mutual_follow = await db.scalar(
                select(Followers).where(
                    Followers.follower_id == user_id,
                    Followers.following_id == current_user.id
                )
            )
            if mutual_follow:
                follow_status = "friend"
            else:
                follow_status = "following"
    
    return {
        "user_id": str(user.id),
        "user_name": user.username,
        "user_nickname": user.nickname,
        "user_avatar": user.avatar_url,
        "user_bio": user.bio,
        "user_follower_quantity": user.follower_quantity,
        "user_following_quantity": user.following_quantity,
        "user_friends_quantity": user.friends_quantity,
        "user_listening_quantity": user.listening_quantity,
        "user_month_listening_quantity": user.month_listening_quantity,
        "follow_status": follow_status  # none | following | friend
    }


@router.get("/get_user/{user_id}")
async def get_user(
    user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_optional_current_user)
):
    """Получение базовой информации о пользователе."""
    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Статус подписки
    follow_status = "none"
    
    if current_user and current_user.id != user_id:
        follow = await db.scalar(
            select(Followers).where(
                Followers.follower_id == current_user.id,
                Followers.following_id == user_id
            )
        )
        
        if follow:
            mutual_follow = await db.scalar(
                select(Followers).where(
                    Followers.follower_id == user_id,
                    Followers.following_id == current_user.id
                )
            )
            if mutual_follow:
                follow_status = "friend"
            else:
                follow_status = "following"
    
    return {
        "user_id": str(user.id),
        "user_nickname": user.nickname,
        "user_avatar": user.avatar_url,
        "follow_status": follow_status
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
    return {
        "followers": [
            {
                "follower_id": str(f.id),
                "nickname": f.nickname,
                "avatar_url": f.avatar_url
            } for f in followers
        ]
    }


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
    return {
        "followings": [
            {
                "following_id": str(f.id),
                "nickname": f.nickname,
                "avatar_url": f.avatar_url
            } for f in following
        ]
    }



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


@router.get("/search")
async def search_users(
        query: str = Query(..., min_length=1, max_length=100, description="Поиск по никнейму или имени пользователя"),
        sort_by: str = Query("relevance", pattern="^(relevance|follower_quantity|created_at)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """
    Поиск пользователей по nickname или username.
    """

    stmt = select(Users)
    search_pattern = f"%{query}%"

    # Ищем по nickname и username (регистронезависимо)
    stmt = stmt.where(
        or_(
            Users.nickname.ilike(search_pattern),
            Users.username.ilike(search_pattern)
        )
    )

    # Сортировка по релевантности
    if sort_by == "relevance":
        stmt = stmt.order_by(
            case(
                # Сначала точное совпадение
                (Users.nickname.ilike(query), 1),
                (Users.username.ilike(query), 2),
                # Начинающиеся с запроса
                (Users.nickname.ilike(f"{query}%"), 3),
                (Users.username.ilike(f"{query}%"), 4),
                # Затем частичное совпадение
                else_=5
            ).asc(),
            # Затем по количеству подписчиков
            desc(Users.follower_quantity)
        )
    elif sort_by == "follower_quantity":
        if sort_order == "desc":
            stmt = stmt.order_by(desc(Users.follower_quantity))
        else:
            stmt = stmt.order_by(Users.follower_quantity)
    elif sort_by == "created_at":
        if sort_order == "desc":
            stmt = stmt.order_by(desc(Users.created_at))
        else:
            stmt = stmt.order_by(Users.created_at)

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    users = result.scalars().all()

    # Формируем ответ
    response = []
    for user in users:
        response.append({
            "id": str(user.id),
            "nickname": user.nickname,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "follower_quantity": user.follower_quantity,
            "following_quantity": user.following_quantity,
            "friends_quantity": user.friends_quantity
        })

    # Подсчёт общего количества
    count_stmt = select(func.count()).select_from(Users).where(
        or_(
            Users.nickname.ilike(search_pattern),
            Users.username.ilike(search_pattern)
        )
    )
    total = await db.execute(count_stmt)

    return {
        "items": response,
        "total": total.scalar_one(),
        "skip": skip,
        "limit": limit,
        "search_query": query
    }