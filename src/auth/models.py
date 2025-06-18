from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class TokenBlocklist(Base):
    """
    블락리스트에 저장된 토큰을 나타내는 모델입니다.
    이 모델은 블락리스트에 저장된 토큰을 관리하기 위해 사용됩니다.
    """

    __tablename__ = "token_blocklist"

    jti: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
