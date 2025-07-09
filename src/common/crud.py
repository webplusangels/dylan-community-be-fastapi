from typing import TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# Generic 타입 정의
T = TypeVar("T")


async def commit_and_refresh(db: AsyncSession, instance: T) -> T:
    """
    데이터베이스에 변경 사항을 커밋하고 인스턴스를 새로 고칩니다.

    모든 모델 타입에 대해 사용할 수 있는 공용 함수입니다.

    :param db: 비동기 데이터베이스 세션
    :param instance: 새로 고칠 인스턴스 (모든 SQLAlchemy 모델)
    :return: 새로 고친 인스턴스
    :raises SQLAlchemyError: DB 관련 예외를 그대로 전파
    """
    try:
        await db.commit()
        await db.refresh(instance)
        return instance
    except SQLAlchemyError:
        await db.rollback()
        raise  # 호출자가 구체적인 예외 처리


async def add_and_commit(db: AsyncSession, instance: T) -> T:
    """
    인스턴스를 추가하고 커밋합니다.

    :param db: 비동기 데이터베이스 세션
    :param instance: 추가할 인스턴스
    :return: 커밋된 인스턴스
    :raises SQLAlchemyError: DB 관련 예외를 그대로 전파
    """
    db.add(instance)
    return await commit_and_refresh(db, instance)


async def delete_and_commit(db: AsyncSession, instance: T) -> bool:
    """
    인스턴스를 삭제하고 커밋합니다.

    :param db: 비동기 데이터베이스 세션
    :param instance: 삭제할 인스턴스
    :return: 성공 시 True
    :raises SQLAlchemyError: DB 관련 예외를 그대로 전파
    """
    await db.delete(instance)
    await db.commit()
    return True
