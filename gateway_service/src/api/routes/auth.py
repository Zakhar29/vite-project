from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from src.api.dependencies import get_current_user, CurrentUser, get_users_client
from src.api.schemas import RegisterRequest, LoginRequest, RefreshResponse
from src.clients.users_service import UsersClient

router = APIRouter(prefix="/auth", tags=["Authentication"])



@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        data: RegisterRequest,
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Регистрация нового пользователя.
    Возвращает access_token и устанавливает refresh_token в cookie.
    """
    result = await users_client.register(
        username=data.username,
        email=data.email,
        password=data.password,
        nickname=data.nickname
    )

    return result


@router.post("/login")
async def login(
        data: LoginRequest,
        response: Response,
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Вход в аккаунт.
    Возвращает access_token в теле ответа,
    а refresh_token устанавливает в HTTP-only cookie.
    """
    result = await users_client.login(
        email=data.email,
        password=data.password
    )

    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")
    token_type = result.get("token_type", "bearer")

    if not access_token:
        raise HTTPException(status_code=500, detail="Invalid response from auth service")

    # Устанавливаем refresh_token в HTTP-only cookie
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # В разработке False, в проде True
            samesite="lax",
            max_age=7 * 24 * 3600  # 7 дней
        )

    return {
        "access_token": access_token,
        "token_type": token_type
    }


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
        request: Request,
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Обновление access_token.
    Refresh_token берётся из HTTP-only cookie.
    """
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    result = await users_client.refresh(refresh_token)

    access_token = result.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="Invalid response from auth service")

    return {
        "access_token": access_token,
        "token_type": result.get("token_type", "bearer")
    }


@router.post("/logout")
async def logout(
        request: Request,
        response: Response,
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Выход из аккаунта.
    Удаляет refresh_token из cookie.
    """
    # Вызываем logout в user_service (если нужно)
    if current_user.token:
        try:
            await users_client.logout(current_user.token)
        except Exception:
            pass

    # Удаляем refresh_token из cookie
    response.delete_cookie("refresh_token")

    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_me(
        current_user: CurrentUser = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе.
    """
    return {
        "id": str(current_user.id),
        "nickname": current_user.nickname,
        "avatar_url": current_user.avatar_url
    }