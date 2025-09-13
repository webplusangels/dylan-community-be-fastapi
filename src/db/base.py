from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.config import settings

if TYPE_CHECKING:
    pass

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


class Base(DeclarativeBase):
    """SQLAlchemy Base 클래스"""

    pass


class SoftDeleteMixin:
    """
    Soft Delete 패턴을 구현하는 Mixin 클래스입니다.

    이 클래스를 상속받은 모델은 실제로 레코드를 삭제하지 않고,
    is_active를 False로 설정하고 deleted_at에 삭제 시간을 기록합니다.

    사용 예시:
        class MyModel(Base, SoftDeleteMixin):
            __tablename__ = "my_table"
            id: Mapped[str] = mapped_column(String(36), primary_key=True)
            name: Mapped[str] = mapped_column(String(100))

    중요: 데이터 조회 시 반드시 active_query() 메서드를 사용하세요.
    """

    is_active: Mapped[bool] = mapped_column(
        Boolean(), default=True, nullable=False, comment="활성 상태 플래그"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="삭제된 시간 (Soft Delete)"
    )

    @classmethod
    def active_query(cls):
        """
        활성화된 레코드만 조회하는 쿼리입니다.

        활성화된 레코드는 is_active가 True이고, deleted_at이 None인 레코드를 의미합니다.

        :return: 활성화된 레코드를 조회하는 SQLAlchemy Select 객체

        사용 예시:
            stmt = User.active_query()
            result = await session.execute(stmt)
            active_users = result.scalars().all()
        """
        return select(cls).where(cls.is_active.is_(True), cls.deleted_at.is_(None))

    @classmethod
    def all_query(cls):
        """
        삭제된 레코드를 포함한 모든 레코드를 조회하는 쿼리입니다.

        관리자 기능이나 데이터 복구 등 특별한 경우에만 사용하세요.

        :return: 모든 레코드를 조회하는 SQLAlchemy Select 객체

        사용 예시:
            # 관리자가 삭제된 사용자를 포함한 모든 사용자 조회
            stmt = User.all_query()
            result = await session.execute(stmt)
            all_users = result.scalars().all()
        """
        return select(cls)

    @classmethod
    def deleted_query(cls):
        """
        삭제된 레코드만 조회하는 쿼리입니다.

        데이터 복구나 감사 목적으로 사용합니다.

        :return: 삭제된 레코드를 조회하는 SQLAlchemy Select 객체

        사용 예시:
            # 삭제된 사용자 조회
            stmt = User.deleted_query()
            result = await session.execute(stmt)
            deleted_users = result.scalars().all()
        """
        return select(cls).where(cls.is_active.is_(False) | cls.deleted_at.is_not(None))

    def soft_delete(self) -> None:
        """
        레코드를 소프트 삭제합니다.

        is_active를 False로 설정하고 deleted_at에 현재 시간을 기록합니다.
        실제 데이터베이스에서 레코드를 삭제하지는 않습니다.

        사용 예시:
            user = await session.get(User, user_id)
            user.soft_delete()
            await session.commit()
        """
        self.is_active = False
        self.deleted_at = func.now()

    def restore(self) -> None:
        """
        소프트 삭제된 레코드를 복원합니다.

        is_active를 True로 설정하고 deleted_at을 None으로 초기화합니다.

        사용 예시:
            user = await session.get(User, user_id)
            user.restore()
            await session.commit()
        """
        self.is_active = True
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """
        레코드가 삭제되었는지 확인합니다.

        :return: 삭제되었으면 True, 아니면 False
        :rtype: bool

        사용 예시:
            if user.is_deleted:
                print("사용자가 삭제되었습니다.")
        """
        return not self.is_active or self.deleted_at is not None
