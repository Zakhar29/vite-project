from sqlalchemy import (
    BigInteger,
    VARCHAR,
    UUID,
    ForeignKey,
    CheckConstraint,
    DateTime,
    Boolean,
    Text,
    SmallInteger,
    PrimaryKeyConstraint,
    Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import uuid6
from src.models.models import Base


class AlbumTypes(Base):
    __tablename__ = "album_types"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)


class AlbumStatuses(Base):
    __tablename__ = "album_statuses"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)


class Albums(Base):
    __tablename__ = "albums"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    author_id: Mapped[uuid6.UUID] = mapped_column(UUID, nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    type: Mapped[int] = mapped_column(SmallInteger, ForeignKey('album_types.id'))
    status: Mapped[int] = mapped_column(SmallInteger, ForeignKey('album_statuses.id'))
    cover_url: Mapped[str] = mapped_column(Text)
    liked_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    follower_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    listening_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)



class LikedAlbums(Base):
    __tablename__ = "liked_albums"

    album_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        ForeignKey('albums.id', ondelete="CASCADE"),
        primary_key=True
    )
    user_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('album_id', 'user_id'),
    )


class AlbumTracks(Base):
    __tablename__ = "album_tracks"

    album_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        ForeignKey('albums.id', ondelete="CASCADE"),  # 🔥 Исправлено
        primary_key=True
    )
    track_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        ForeignKey('tracks.id', ondelete="CASCADE"),   # 🔥 Исправлено
        primary_key=True
    )
    author_attention: Mapped[bool] = mapped_column(Boolean, default=False)
    number: Mapped[int] = mapped_column(
        SmallInteger,
        CheckConstraint("number > 0")  # 🔥 sqltext= не нужен в CheckConstraint
    )

    __table_args__ = (
        PrimaryKeyConstraint('album_id', 'track_id'),
   )


class AlbumFeaturing(Base):
    __tablename__ = "album_featuring"

    album_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        ForeignKey('albums.id', ondelete="CASCADE"),  # 🔥 Исправлено
        primary_key=True
    )
    user_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        primary_key=True
    )

    __table_args__ = (
        PrimaryKeyConstraint('album_id', 'user_id'),
    )


class AlbumFollows(Base):
    __tablename__ = "album_follows"

    album_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        ForeignKey('albums.id', ondelete="CASCADE"),  # 🔥 Исправлено
        primary_key=True
    )
    user_id: Mapped[uuid6.UUID] = mapped_column(
        UUID, 
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    __table_args__ = (
        PrimaryKeyConstraint('album_id', 'user_id'),
    )
