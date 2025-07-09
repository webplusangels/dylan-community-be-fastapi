import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Index, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.sql import func

from src.db.base import Base

if TYPE_CHECKING:
    from src.comments.models import PostComment
    from src.likes.models import PostLike
    from src.posts.models import Post


class User(Base):
    """
    User 모델 클래스입니다.
    이 클래스는 SQLAlchemy를 사용해 DB 테이블을 정의합니다.
    """

    __tablename__ = "users"

    __exclude_fields__ = {
        "hashed_password",
        "token_version",
    }

    __table_args__ = (Index("idx_user_active_deleted", "is_active", "deleted_at"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_version: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")
    likes: Mapped[list["PostLike"]] = relationship("PostLike", back_populates="user")
    comments: Mapped[list["PostComment"]] = relationship(
        "PostComment", back_populates="author"
    )

    @classmethod
    def active_query(cls):
        """
        활성화된 사용자만 조회하는 쿼리입니다.
        deleted_at이 None이고 is_active가 True인 사용자만 반환합니다.

        :return: 활성화된 사용자를 조회하는 SQLAlchemy 쿼리 객체
        """
        return select(cls).where(cls.deleted_at.is_(None), cls.is_active.is_(True))

    @classmethod
    def with_posts(cls, stmt):
        """
        사용자와 작성한 게시글 정보를 eager loading하는 쿼리입니다.

        :param stmt: SQLAlchemy 쿼리 객체
        :return: 작성한 게시글 정보를 포함한 사용자 쿼리 객체
        """
        return stmt.options(selectinload(cls.posts))

    @classmethod
    def with_likes(cls, stmt):
        """
        사용자와 좋아요한 게시글 정보를 eager loading하는 쿼리입니다.

        :param stmt: SQLAlchemy 쿼리 객체
        :return: 좋아요한 게시글 정보를 포함한 사용자 쿼리 객체
        """
        return stmt.options(selectinload(cls.likes))

    @classmethod
    def with_comments(cls, stmt):
        """
        사용자와 작성한 댓글 정보를 eager loading하는 쿼리입니다.

        :param stmt: SQLAlchemy 쿼리 객체
        :return: 작성한 댓글 정보를 포함한 사용자 쿼리 객체
        """
        return stmt.options(selectinload(cls.comments))

    @classmethod
    def with_all(cls, stmt):
        """
        사용자와 작성한 게시글, 좋아요한 게시글, 작성한 댓글 정보를 모두 eager loading하는 쿼리입니다.

        :param stmt: SQLAlchemy 쿼리 객체
        :return: 모든 관련 정보를 포함한 사용자 쿼리 객체
        """
        return stmt.options(
            selectinload(cls.posts), selectinload(cls.likes), selectinload(cls.comments)
        )
