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

app = FastAPI(title="User Service API")

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


# Аутентификация
@app.post("/api/auth/register", response_model=Token)
async def register(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(db, redis)
    return await auth_service.register(user_data)


@app.post("/api/auth/login", response_model=Token)
async def login(
        login_data: UserLogin,
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(db, redis)
    return await auth_service.login(login_data)


@app.post("/api/auth/refresh", response_model=Token)
async def refresh(
        refresh_token: str,
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(db, redis)
    return await auth_service.refresh_tokens(refresh_token)


@app.post("/api/auth/logout")
async def logout(
        current_user: Users = Depends(get_current_user),
        redis=Depends(get_redis_client)
):
    auth_service = AuthService(None, redis)
    await auth_service.logout(str(current_user.id))
    return {"message": "Successfully logged out"}


# Пользователи
@app.get("/api/users/me", response_model=UserResponse)
async def get_me(current_user: Users = Depends(get_current_user)):
    return current_user


# Подписки
@app.post("/api/users/{user_id}/follow")
async def follow_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # Проверяем существование пользователя
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

    # Обновляем счетчики
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


@app.delete("/api/users/{user_id}/follow")
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

    # Обновляем счетчики
    await db.execute(
        update(Users).where(Users.id == current_user.id).values(
            following_quantity=Users.following_quantity - 1
        )
    )
    await db.execute(
        update(Users).where(Users.id == user_id).values(
            follower_quantity=Users.follower_quantity - 1
        )
    )

    await db.commit()
    return {"message": "Successfully unfollowed"}


@app.get("/api/users/{user_id}/followers")
async def get_followers(
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    result = await db.execute(
        select(Users).join(Followers, Followers.follower_id == Users.id)
        .where(Followers.following_id == user_id)
        .offset(skip).limit(limit)
    )
    followers = result.scalars().all()
    return followers


@app.get("/api/users/{user_id}/following")
async def get_following(
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    result = await db.execute(
        select(Users).join(Followers, Followers.following_id == Users.id)
        .where(Followers.follower_id == user_id)
        .offset(skip).limit(limit)
    )
    following = result.scalars().all()
    return following


# Друзья (взаимные подписки)
@app.post("/api/users/{user_id}/friend")
async def add_friend(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    # Проверяем, что пользователи подписаны друг на друга
    follow1 = await db.execute(
        select(Followers).where(
            Followers.follower_id == current_user.id,
            Followers.following_id == user_id
        )
    )
    follow2 = await db.execute(
        select(Followers).where(
            Followers.follower_id == user_id,
            Followers.following_id == current_user.id
        )
    )

    if not follow1.scalar_one_or_none() or not follow2.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Must be mutual followers to become friends")

    # Проверяем, не друзья ли уже
    existing = await db.execute(
        select(Friends).where(
            ((Friends.follower_id == current_user.id) & (Friends.following_id == user_id)) |
            ((Friends.follower_id == user_id) & (Friends.following_id == current_user.id))
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already friends")

    # Генерируем общий ключ для чата
    import secrets
    chat_key = secrets.token_urlsafe(32)

    # Создаем запись о дружбе
    friendship = Friends(
        follower_id=current_user.id,
        following_id=user_id,
        chat_key=chat_key
    )
    db.add(friendship)

    # Обновляем счетчики
    await db.execute(
        update(Users).where(Users.id == current_user.id).values(
            friends_quantity=Users.friends_quantity + 1
        )
    )
    await db.execute(
        update(Users).where(Users.id == user_id).values(
            friends_quantity=Users.friends_quantity + 1
        )
    )

    await db.commit()
    return {"message": "Friend added", "chat_key": chat_key}
