import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.sql import func

from src.db.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from src.comments.models import PostComment
    from src.likes.models import PostLike
    from src.users.models import User


class Post(Base, SoftDeleteMixin):
    """
    Post 모델 클래스입니다.
    이 클래스는 SQLAlchemy를 사용해 DB 테이블을 정의합니다.
    """

    __tablename__ = "posts"

    __table_args__ = (
        Index("idx_posts_user_created", "user_id", "created_at"),
        Index(
            "idx_posts_created_desc",
            "created_at",
            postgresql_using="btree",
            postgresql_ops={"created_at": "desc"},
        ),
        CheckConstraint("length(title) > 0", name="check_title_not_empty"),
        CheckConstraint("length(content) > 0", name="check_content_not_empty"),
        CheckConstraint(
            "views >= 0", name="check_views_non_negative"
        ),  # 조회수는 음수가 될 수 없음
    )

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

    @classmethod
    def public_query(cls):
        """
        공개된 게시글만 조회하는 쿼리입니다.
        일반 사용자들이 볼 수 있는 게시글입니다.
        """
        return cls.active_query()

    @classmethod
    def all_non_deleted_query(cls):
        """
        삭제되지 않은 모든 게시글을 조회하는 쿼리입니다.
        deleted_at이 None인 게시글을 의미합니다.
        관리자 또는 특정 권한을 가진 사용자가 삭제되지 않은 게시글을 조회할 때 사용됩니다.

        :return: 삭제되지 않은 게시글을 조회하는 SQLAlchemy 쿼리 객체
        """
        return select(cls).where(cls.deleted_at.is_(None))

    @classmethod
    def with_author(cls, stmt):
        """
        게시글과 작성자 정보를 eager loading하는 쿼리입니다.

        :param stmt: SQLAlchemy 쿼리 객체
        :return: 작성자 정보를 포함한 게시글 쿼리 객체
        """
        return stmt.options(selectinload(cls.author))
