from sqlalchemy import (
    BigInteger,
    DateTime,
    Text,
    SmallInteger,
    VARCHAR,
    UUID,
    ForeignKey,
    Numeric,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import uuid6
from decimal import Decimal
from example.infrastucture.db.postgres.models import Base


class Tracks(Base):
    __tablename__ = "tracks"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    track_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    author_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'))
    title: Mapped[str] = mapped_column(VARCHAR(100), unique=True, nullable=False)
    track_text: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    bpm: Mapped[Decimal] = mapped_column(
        Numeric(precision=6, scale=2),
        CheckConstraint(sqltext="bpm >= 10 AND bpm <= 1000"),
        nullable=False
    )
    liked_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    listening_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class LikedTracks(Base):
    __tablename__ = "liked_tracks"

    track_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('tracks.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ListeningTracks(Base):
    __tablename__ = "listening_tracks"

    track_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('tracks.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class TrackFeaturing(Base):
    __tablename__ = "track_featuring"

    track_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('tracks.id'), ondelete="CASCADE")
    user_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")


class Genres(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)


class GenreParents(Base):
    __tablename__ = "genre_parents"

    child_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('genres.id'), ondelete="CASCADE")
    parent_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('genres.id'), ondelete="CASCADE")

    __table_args__ = (
        CheckConstraint("child_id != parent_id", name="no_self_reference"),
    )


class TrackGenres(Base):
    __tablename__ = "track_genres"

    genre_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('genres.id'), ondelete="CASCADE")
    track_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('tracks.id'), ondelete="CASCADE")
