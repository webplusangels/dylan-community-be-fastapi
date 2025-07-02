# PostLike.pyi
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped

class PostLike:
    __tablename__: str

    post_id: Mapped[str]
    user_id: Mapped[str]
    deleted_at: Mapped[datetime]

    post: Mapped[Any]  # Post
    user: Mapped[Any]  # User

    def __init__(self, **kwargs: Any) -> None: ...
