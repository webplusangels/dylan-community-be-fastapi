import asyncio
import sys

from src.core.config import settings
from src.db.base import Base, engine


async def init_database(drop_existing: bool = True) -> None:
    """
    데이터베이스 테이블을 생성합니다.

    :param drop_existing: 기존 테이블을 삭제할지 여부
    :raises Exception: 데이터베이스 초기화 중 오류 발생 시
    """

    from src.auth import models as auth_models  # noqa: F401
    from src.users import models as user_models  # noqa: F401

    print(f"데이터베이스 연결: {settings.DATABASE_URL}")

    if not settings.DEBUG_MODE and drop_existing:
        confirm = input("프로덕션 환경에서 테이블을 삭제하시겠습니까? (y/n): ")
        if confirm.lower() != "y":
            print("작업이 취소되었습니다.")
            return

    try:
        async with engine.begin() as conn:
            if drop_existing:
                print("기존 테이블을 삭제하는 중...")
                await conn.run_sync(Base.metadata.drop_all)
                print("기존 테이블을 삭제했습니다.")

            print("새로운 테이블을 생성하는 중...")
            await conn.run_sync(Base.metadata.create_all)
            print("새로운 테이블을 생성했습니다.")

            tables = list(Base.metadata.tables.keys())
            print(f"생성된 테이블: {', '.join(tables)}")

    except Exception as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
        raise
    finally:
        print("데이터베이스 초기화 작업이 완료되었습니다.")


async def create_only() -> None:
    """테이블을 생성하지만 기존 테이블은 삭제하지 않습니다."""
    await init_database(drop_existing=False)


def main() -> None:
    """메인 실행 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "--create-only":
        # python src/scripts/init_db.py --create-only
        print("테이블 생성 모드로 실행합니다.")
        asyncio.run(create_only())
    else:
        # python src/scripts/init_db.py
        print("데이터베이스 초기화를 시작합니다.")
        asyncio.run(init_database())


if __name__ == "__main__":
    main()
