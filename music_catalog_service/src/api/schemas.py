from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
import uuid


class AlbumCreateDraft(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    type: int = None
    cover_url: Optional[str] = None


class AlbumUpdateDraft(BaseModel):
    title: Optional[str] = None
    cover_url: Optional[str] = None
    type: Optional[str] = None


class TrackCreateDraft(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    text: Optional[str] = ""
    bpm: Optional[Decimal] = None


class TrackUpdateDraft(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    bpm: Optional[Decimal] = None


class AlbumResponse(BaseModel):
    id: uuid.UUID
    title: str
    type: str
    status: str
    cover_url: Optional[str]
    track_count: int

    class Config:
        from_attributes = True

class GenreIdsPayload(BaseModel):
    genre_ids: list[int]
