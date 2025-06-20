import asyncio

from src.db.base import engine
from src.users.models import Base


async def init_database():
    """데이터베이스 테이블을 생성합니다."""
    async with engine.begin() as conn:
        # 모든 테이블 삭제 후 재생성
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다!")


if __name__ == "__main__":
    asyncio.run(init_database())

# poetry run python src/scripts/init_db.py
# 위 명령어로 데이터베이스를 초기화할 수 있습니다.
