from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, and_

import uuid

from src.db.postgres_engine import get_db, init_db
from src.services.auth_service import AuthService
from src.api.dependencies import get_current_user, get_redis_client
from src.api.schemas import UserCreate, UserLogin, UserResponse, Token, UserList
from src.models.users_models import Users, Followers, Friends

router = APIRouter(
    prefix="/follow",
    tags=["User Follows"],
)

# Подписки
@router.post("/{user_id}")
async def follow_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # ===== ИСПРАВЛЕНО: используем await для execute, потом scalar_one_or_none =====
    result = await db.execute(select(Users).where(Users.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, не подписан ли уже
    existing = await db.execute(
        select(Followers).where(
            Followers.follower_id == current_user.id,
            Followers.following_id == user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already following")

    # Создаем подписку
    follow = Followers(follower_id=current_user.id, following_id=user_id)
    db.add(follow)

    # Проверяем, есть ли взаимная подписка (друзья)
    friendship = await db.execute(
        select(Followers).where(
            Followers.follower_id == user_id,
            Followers.following_id == current_user.id
        )
    )
    if friendship.scalar_one_or_none():
        # Добавляем в друзья
        friend = Friends(friend1=current_user.id, friend2=user_id)
        db.add(friend)
        
        # Обновляем счетчики друзей
        await db.execute(
            update(Users)
            .where(Users.id == current_user.id)
            .values(friends_quantity=Users.friends_quantity + 1)
        )
        await db.execute(
            update(Users)
            .where(Users.id == user_id)
            .values(friends_quantity=Users.friends_quantity + 1)
        )

    # Обновляем счетчики подписок
    await db.execute(
        update(Users)
        .where(Users.id == current_user.id)
        .values(following_quantity=Users.following_quantity + 1)
    )

    await db.execute(
        update(Users)
        .where(Users.id == user_id)
        .values(follower_quantity=Users.follower_quantity + 1)
    )

    await db.commit()
    return {"message": "Successfully followed"}


@router.delete("/{user_id}")
async def unfollow_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    # ===== ИСПРАВЛЕНО: используем await для execute =====
    result = await db.execute(
        select(Followers).where(
            Followers.follower_id == current_user.id,
            Followers.following_id == user_id
        )
    )
    follow = result.scalar_one_or_none()

    if not follow:
        raise HTTPException(status_code=400, detail="Not following")

    await db.delete(follow)

    # Проверяем, были ли друзьями
    friend = await db.execute(
        select(Friends).where(
            or_(
                and_(Friends.friend1 == current_user.id, Friends.friend2 == user_id),
                and_(Friends.friend1 == user_id, Friends.friend2 == current_user.id)
            )
        )
    )
    if friend.scalar_one_or_none():
        await db.delete(friend.scalar_one())
        
        # Обновляем счетчики друзей
        await db.execute(
            update(Users)
            .where(Users.id == current_user.id)
            .values(friends_quantity=Users.friends_quantity - 1)
        )
        await db.execute(
            update(Users)
            .where(Users.id == user_id)
            .values(friends_quantity=Users.friends_quantity - 1)
        )
    
    # Обновляем счетчики подписок
    await db.execute(
        update(Users)
        .where(Users.id == current_user.id)
        .values(following_quantity=Users.following_quantity - 1)
    )
    
    await db.execute(
        update(Users)
        .where(Users.id == user_id)
        .values(follower_quantity=Users.follower_quantity - 1)
    )

    await db.commit()
    return {"message": "Successfully unfollowed"}


