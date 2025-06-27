import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.base import Base

if TYPE_CHECKING:
    from src.comments.models import PostComment
    from src.likes.models import PostLike
    from src.users.models import User


class Post(Base):
    """
    Post 모델 클래스입니다.
    이 클래스는 SQLAlchemy를 사용해 DB 테이블을 정의합니다.
    """

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    image_path: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    views: Mapped[int] = mapped_column(Integer(), default=0, nullable=False)
    likes: Mapped[int] = mapped_column(Integer(), default=0, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer(), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author: Mapped["User"] = relationship("User", back_populates="posts")
    post_likes: Mapped[list["PostLike"]] = relationship(
        "PostLike", back_populates="post", cascade="all, delete-orphan"
    )
    post_comments: Mapped[list["PostComment"]] = relationship(
        "PostComment", back_populates="post", cascade="all, delete-orphan"
    )
