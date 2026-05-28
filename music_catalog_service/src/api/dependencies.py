from fastapi import Depends, HTTPException, Header
from pydantic import BaseModel, UUID
from jose import jwt, JWTError
from config import settings


class CurrentUser(BaseModel):
    id: UUID
    # role: str = "user"  # можно добавить при необходимости


async def get_current_user(
        authorization: str = Header(...)
) -> CurrentUser:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(401, "Invalid authentication scheme")

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")  # или "user_id", зависит от вашего Auth-сервиса
        if not user_id:
            raise HTTPException(401, "Invalid token payload")

        return CurrentUser(id=UUID(user_id))
    except JWTError as e:
        raise HTTPException(401, f"Token verification failed: {str(e)}")
    except Exception:
        raise HTTPException(401, "Invalid authorization header")
