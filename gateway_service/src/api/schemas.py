from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
import uuid

class TrackItem(BaseModel):
    title: str
    bpm: float
    genres: list[int] = []
    text: str = ""
    author_attention: bool = False

class MediaItem(BaseModel):
    type: str  # "image", "video", "audio"
    url: str

class PostCreateRequest(BaseModel):
    text: str = ""
    media: list[MediaItem] = []

class PostCommentCreate(BaseModel):
    comment: str

class PostCommentUpdate(BaseModel):
    comment: str

class CommentReplyCreate(BaseModel):
    comment: str
    track_timecode: Optional[int] = None

class TrackCommentCreate(BaseModel):
    comment: str
    track_timecode: Optional[int] = None

class TrackCommentUpdate(BaseModel):
    comment: str
    track_timecode: Optional[int] = None


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    nickname: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileNicknameUpdate(BaseModel):
    nickname: str


class ProfileUsernameUpdate(BaseModel):
    username: str


class ProfileBioUpdate(BaseModel):
    bio: str = ""


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TrackRecommendationResponse(BaseModel):
    track_id: str
    title: str
    album_id: Optional[str] = None
    cover_url: Optional[str] = None
    author_id: str
    author_nickname: Optional[str] = None
    author_avatar: Optional[str] = None
    feats: list[str] = []
    track_url: str
    bpm: Optional[float] = None
    genres: list[str] = []
    liked_quantity: int = 0
    comments_quantity: int = 0
    listening_quantity: int = 0
    published_at_formatted: Optional[str] = None
    published_at_raw: Optional[str] = None


class AlbumRecommendationResponse(BaseModel):
    id: str
    title: str
    author_id: str
    author_nickname: Optional[str] = None
    author_avatar: Optional[str] = None
    cover_url: Optional[str] = None
    type_id: Optional[int] = None
    type: Optional[str] = None
    genres: list[str] = []
    liked_quantity: int = 0
    follower_quantity: int = 0
    listening_quantity: int = 0
    comments_quantity: int = 0
    tracks_count: int = 0
    published_at_formatted: Optional[str] = None
    published_at_raw: Optional[str] = None


class RecommendationsResponse(BaseModel):
    items: list
    total: int
    type: str  # "global", "personalized", "cold_start"