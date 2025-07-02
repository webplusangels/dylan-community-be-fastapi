# PostLike.pyi
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped

class PostComment:
    __tablename__: str

    id: Mapped[str]
    post_id: Mapped[str]
    user_id: Mapped[str]
    content: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None]

    post: Mapped[Any]  # Post
    author: Mapped[Any]  # User

    def __init__(self, **kwargs: Any) -> None: ...
