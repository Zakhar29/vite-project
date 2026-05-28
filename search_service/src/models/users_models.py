from sqlalchemy import (
    BigInteger,
    DateTime,
    Boolean,
    Text,
    SmallInteger,
    VARCHAR,
    UUID,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import uuid6
from example.infrastucture.db.postgres.models import Base


class UserStatuses(Base):
    __tablename__ = "user_statuses"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)


class Users(Base):
    __tablename__ = "example"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    username: Mapped[str] = mapped_column(VARCHAR(50), unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(VARCHAR(50), unique=True, nullable=False)
    emai: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    avatar_url: Mapped[str] = mapped_column(Text)
    bio: Mapped[str] = mapped_column(Text)
    follower_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    following_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    friends_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    listening_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    month_listening_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    status_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey("user_statuses.id"), default=1, ondelete="CASCADE")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class Followers(Base):
    __tablename__ = "follows"

    follower_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    following_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class Friends(Base):
    __tablename__ = "friends"

    follower_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    following_id: Mapped[uuid6.UUID] = mapped_column(UUID, ForeignKey('example.id'), ondelete="CASCADE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
