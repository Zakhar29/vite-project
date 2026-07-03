from sqlalchemy import (
    BigInteger,
    DateTime,
    Boolean,
    Text,
    SmallInteger,
    VARCHAR,
    UUID,
    ForeignKey,
    PrimaryKeyConstraint,
    Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
import uuid6
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserStatuses(Base):
    __tablename__ = "user_statuses"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    username: Mapped[str] = mapped_column(VARCHAR(50), unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(VARCHAR(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(Text, nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    follower_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    following_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    friends_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    listening_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    month_listening_quantity: Mapped[int] = mapped_column(BigInteger, default=0)
    status_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey("user_statuses.id", ondelete="CASCADE"), default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Followers(Base):
    __tablename__ = "follows"
    __table_args__ = (
        PrimaryKeyConstraint('follower_id', 'following_id'),
        Index('idx_follower_id', 'follower_id'),
        Index('idx_following_id', 'following_id'),
    )

    follower_id: Mapped[uuid6.UUID] = mapped_column(  # изменено
        UUID,
        ForeignKey('users.id', ondelete="CASCADE")
    )
    following_id: Mapped[uuid6.UUID] = mapped_column(  # изменено
        UUID,
        ForeignKey('users.id', ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Friends(Base):
    __tablename__ = "friends"
    __table_args__ = (
        PrimaryKeyConstraint('friend1', 'friend2'),
        Index('idx_friends_follower_id', 'friend1'),
        Index('idx_friends_following_id', 'friend2'),
    )

    friend1: Mapped[uuid6.UUID] = mapped_column(  # изменено
        UUID,
        ForeignKey('users.id', ondelete="CASCADE")
    )
    friend2: Mapped[uuid6.UUID] = mapped_column(  # изменено
        UUID,
        ForeignKey('users.id', ondelete="CASCADE")
    )
    chat_key: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
