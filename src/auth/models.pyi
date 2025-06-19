from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy.orm import Mapped, declarative_base

T = TypeVar("T")
Base = declarative_base()

class TokenBlocklist(Base):
    jti: Mapped[str]
    expires_at: Mapped[datetime]

    # Pyre에게 __init__ 메서드가 어떤 키워드 인수든 받을 수 있다고 알려줍니다.
    def __init__(self, **kwargs: Any) -> None: ...
