from datetime import datetime
from typing import Any

from sqlalchemy import Select
from sqlalchemy.orm import Mapped

from src.posts.models import Post

class User:
    __tablename__: str

    id: Mapped[str]
    email: Mapped[str]
    username: Mapped[str]
    hashed_password: Mapped[str]
    profile_image_path: Mapped[str | None]
    token_version: Mapped[int]
    is_active: Mapped[bool]
    is_admin: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None]

    posts: Mapped[list[Any]]
    likes: Mapped[list[Any]]
    comments: Mapped[list[Any]]

    @classmethod
    def active_query(cls) -> Select[tuple[Post]]: ...
    @classmethod
    def with_author(cls, stmt: Select[tuple[Post]]) -> Select[tuple[Post]]: ...
    @classmethod
    def public_query(cls) -> Select[tuple[Post]]: ...
    @classmethod
    def all_non_deleted_query(cls) -> Select[tuple[Post]]: ...

    # Pyre에게 __init__ 메서드가 어떤 키워드 인수든 받을 수 있다고 알려줍니다.
    def __init__(self, **kwargs: Any) -> None: ...
