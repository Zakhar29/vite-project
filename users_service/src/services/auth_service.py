from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import redis
import uuid
from jose import jwt, JWTError
from datetime import datetime, timedelta

from src.models.users_models import Users
from config import settings
from passlib.context import CryptContext


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Создание access token с помощью jose"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Создание refresh token с помощью jose"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class AuthService:
    def __init__(self, db: AsyncSession, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client

    async def register(self, user_data) -> dict:
        """Регистрация нового пользователя"""
        # Проверка существования пользователя
        existing_user = await self.db.execute(
            select(Users).where(
                (Users.email == user_data.email) | (Users.username == user_data.username)
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )

        # Создание пользователя
        new_user = Users(
            username=user_data.username,
            nickname=user_data.nickname,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # Создание токенов
        token_data = {"user_id": str(new_user.id), "email": new_user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)


        # Сохранение refresh token в Redis
        self.redis.setex(
            f"refresh_token:{new_user.id}",
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            refresh_token
        )

        # Сохранение изменений в БД (access_token)
        await self.db.commit()

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def login(self, login_data) -> dict:
        """Авторизация пользователя"""
        # Поиск пользователя
        result = await self.db.execute(
            select(Users).where(Users.email == login_data.email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        # Создание токенов
        token_data = {"user_id": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Сохраняем refresh token в Redis
        self.redis.setex(
            f"refresh_token:{user.id}",
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            refresh_token
        )

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh_tokens(self, refresh_token: str) -> dict:
        """Обновление токенов"""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("user_id")
        stored_token = self.redis.get(f"refresh_token:{user_id}")

        if not stored_token or stored_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or invalid"
            )

        # Получаем пользователя
        user_result = await self.db.execute(
            select(Users).where(Users.id == uuid.UUID(user_id))
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Создаем новые токены
        token_data = {"user_id": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)


        return {"access_token": access_token}

    async def logout(self, user_id: str):
        """Выход пользователя"""
        self.redis.delete(f"refresh_token:{user_id}")
        return {"message": "Successfully logged out"}
