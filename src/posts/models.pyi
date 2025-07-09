from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped

class Post:
    __tablename__: str

    id: Mapped[str]
    user_id: Mapped[str]
    title: Mapped[str]
    content: Mapped[str]
    image_path: Mapped[str | None]
    views: Mapped[int]
    likes: Mapped[int]
    comments_count: Mapped[int]
    is_active: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None]

    author: Mapped[Any]  # User
    post_likes: Mapped[list[Any]]  # PostLike
    post_comments: Mapped[list[Any]]  # PostComment

    def __init__(self, **kwargs: Any) -> None: ...
