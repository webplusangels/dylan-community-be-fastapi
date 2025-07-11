import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.sql import func

from src.db.base import Base

if TYPE_CHECKING:
    from src.posts.models import Post
    from src.users.models import User


class PostComment(Base):
    """
    PostComment 모델 클래스입니다.
    이 클래스는 SQLAlchemy를 사용해 DB 테이블을 정의합니다.
    """

    __tablename__ = "post_comments"

    __table_args__ = (
        Index("idx_post_comments_post_id", "post_id"),
        Index("idx_post_comments_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    post_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("posts.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 관계 설정
    post: Mapped["Post"] = relationship("Post", back_populates="post_comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")

    @classmethod
    def active_query(cls):
        """
        활성화된 댓글만 조회하는 쿼리

        :return: 활성화된 댓글 쿼리
        """
        return select(cls).where(cls.is_active.is_(True), cls.deleted_at.is_(None))

    @classmethod
    def public_query(cls):
        """
        활성화된 댓글과 삭제되지 않은 댓글만 조회하는 쿼리

        :return: 활성화되고 삭제되지 않은 댓글 쿼리
        """
        return cls.active_query()

    @classmethod
    def with_author(cls, stmt):
        """
        댓글과 작성자 정보를 함께 조회하는 쿼리

        :param stmt: SQLAlchemy 쿼리 객체
        :return: 작성자 정보를 포함한 댓글 쿼리 객체
        """
        return stmt.options(selectinload(cls.author))
