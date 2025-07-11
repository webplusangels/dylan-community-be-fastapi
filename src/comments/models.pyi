# PostLike.pyi
from datetime import datetime
from typing import Any

from sqlalchemy import Select
from sqlalchemy.orm import Mapped

class PostComment:
    __tablename__: str

    id: Mapped[str]
    post_id: Mapped[str]
    user_id: Mapped[str]
    content: Mapped[str]
    is_active: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None]

    post: Mapped[Any]  # Post
    author: Mapped[Any]  # User

    @classmethod
    def active_query(cls) -> Select[tuple[PostComment]]: ...
    @classmethod
    def public_query(cls) -> Select[tuple[PostComment]]: ...
    @classmethod
    def with_author(
        cls, stmt: Select[tuple[PostComment]]
    ) -> Select[tuple[PostComment]]: ...
    def __init__(self, **kwargs: Any) -> None: ...
