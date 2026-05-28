from sqlalchemy import (
    BigInteger,
    DateTime,
    Boolean,
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
from db.postgres.models import Base


class AlbumTypes(Base):
    __tablename__ = "album_types"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)


class Albums(Base):
    __tablename__ = "albums"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    author_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'))
    title: Mapped[str] = mapped_column(VARCHAR(100), unique=True, nullable=False)
    album_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    type: Mapped[int] = mapped_column(SmallInteger, ForeignKey('album_types.id'))
    cover_url: Mapped[str] = mapped_column(Text, unique=True)
    liked_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    follower_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    listening_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class LikedAlbums(Base):
    __tablename__ = "liked_albums"

    album_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('albums.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlbumTracks(Base):
    __tablename__ = "album_tracks"

    album_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('albums.id'), ondelete="CASCADE")
    track_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('tracks.id'), ondelete="CASCADE")
    author_attention: Mapped[bool] = mapped_column(Boolean, default=False)
    number: Mapped[int] = mapped_column(
        SmallInteger,
        CheckConstraint(sqltext="number > 0")
    )


class AlbumFeaturing(Base):
    __tablename__ = "album_featuring"

    album_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('albums.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")


class AlbumFollows(Base):
    __tablename__ = "album_follows"

    album_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('albums.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
