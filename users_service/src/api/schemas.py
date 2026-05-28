from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid  # изменено с uuid6


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class UserCreate(BaseSchema):
    username: str = Field(..., max_length=50)
    nickname: str = Field(..., max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=72)

class UserLogin(BaseSchema):
    email: str
    password: str


class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseSchema):
    id: uuid.UUID
    username: str
    nickname: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    follower_quantity: int
    following_quantity: int
    friends_quantity: int
    listening_quantity: int
    month_listening_quantity: int
    status_id: int
    is_active: bool
    created_at: datetime


class UserList(BaseSchema):
    user_ids: list[uuid.UUID]
