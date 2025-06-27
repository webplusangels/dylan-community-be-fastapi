from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.posts.models import Post
    from src.users.models import User


class PostLike(Base):
    """게시글 좋아요 모델"""

    __tablename__ = "post_likes"

    post_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("posts.id"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), primary_key=True
    )

    # 관계 설정
    post: Mapped["Post"] = relationship("Post", back_populates="post_likes")
    user: Mapped["User"] = relationship("User", back_populates="likes")
