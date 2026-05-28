from sqlalchemy import (
    BigInteger,
    DateTime,
    Text,
    SmallInteger,
    VARCHAR,
    UUID,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import uuid6
from src.models.models import Base


class Playlists(Base):
    __tablename__ = "playlists"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    author_id: Mapped[uuid6.UUID] = mapped_column(UUID, nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(100), unique=True, nullable=False)
    playlists_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    cover_url: Mapped[str] = mapped_column(Text, unique=True)
    liked_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    follower_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class LikedPlaylists(Base):
    __tablename__ = "liked_playlists"

    playlist_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('playlists.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PlaylistTracks(Base):
    __tablename__ = "playlist_tracks"

    playlist_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('playlists.id'), ondelete="CASCADE")
    track_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('tracks.id'), ondelete="CASCADE")
    number: Mapped[int] = mapped_column(
        SmallInteger,
        CheckConstraint(sqltext="number > 0")
    )


class PlaylistFeaturing(Base):
    __tablename__ = "playlist_featuring"

    playlist_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('playlists.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, nullable=False)


class PlaylistFollows(Base):
    __tablename__ = "playlist_follows"

    playlist_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('playlists.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
