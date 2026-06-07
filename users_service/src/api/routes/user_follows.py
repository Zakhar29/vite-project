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


    follow = Followers(follower_id=current_user.id, following_id=user_id)
    db.add(follow)

    friendship = await db.execute(
        select(Followers).where(
            Followers.follower_id == user_id,
            Followers.following_id == current_user.id
        )
    ).scalar_one_or_none()
    
    if friendship:
        friend = Friends(friend1=current_user.id, friend2=user_id)
        db.add(friend)
        await db.execute(
            update(Users).where(Users.id == current_user.id).values(
                friends_quantity=Users.friends_quantity + 1,
            )
        )
        await db.execute(
            update(Users).where(Users.id == user_id).values(
                friends_quantity=Users.friends_quantity + 1
            )
        )
    await db.execute(
        update(Users).where(Users.id == current_user.id).values(
            following_quantity=Users.following_quantity + 1
        )
    )

    await db.execute(
        update(Users).where(Users.id == user_id).values(
            follower_quantity=Users.follower_quantity + 1
        )
    )

    await db.commit()
    return {"message": "Successfully followed"}


@router.delete("/{user_id}")
async def unfollow_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
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

    friend = await db.execute(
        select(Friends).where(
            or_(
                and_(Friends.friend1 == current_user.id, Friends.friend2 == user_id),
                and_(Friends.friend1 == user_id, Friends.friend2 == current_user.id)
            )
        )
    ).scalar_one_or_none()

    if friend:
        await db.delete(friend)
        await db.execute(
            update(Users).where(Users.id == current_user.id).values(
                friends_quantity=Users.friends_quantity - 1
            )
        )
        await db.execute(
            update(Users).where(Users.id == user_id).values(
                friends_quantity=Users.friends_quantity - 1
            )
        )
    
    await db.execute(
        update(Users).where(Users.id == current_user.id).values(
            following_quantity=Users.following_quantity - 1,
        )
    )
    
    await db.execute(
        update(Users).where(Users.id == user_id).values(
            follower_quantity=Users.follower_quantity - 1
        )
    )


    await db.commit()
    return {"message": "Successfully unfollowed"}



