from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.base import Base
from src.db.session import get_async_db

# pytest를 위한 애플리케이션 및 설정 관련 모듈
from src.main import app

# 사용자 모델 및 CRUD 관련 모듈
from src.users.crud import create_user
from src.users.models import User
from src.users.schemas import UserCreate

# 테스트용 데이터베이스 엔진 생성
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# TestClient 설정


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    동기식 API 요청을 위한 TestClient 인스턴스를 제공합니다.
    """
    with TestClient(app) as client:
        yield client


# httpx AsyncClient 설정
@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    비동기 API 요청을 위한 AsyncClient 인스턴스를 제공합니다.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


# 테스트 데이터베이스 설정
@pytest.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    테스트용 비동기 데이터베이스 세션을 생성하고, 테스트 후 롤백합니다.
    get_async_db 의존성을 오버라이드하여 테스트 세션을 사용합니다.
    """
    # 테스트용 테이블 생성
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 테스트용 세션 생성
    async_session = TestAsyncSessionLocal()

    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    # get_async_db 의존성 오버라이드
    app.dependency_overrides[get_async_db] = override_get_async_db

    # 테스트 세션을 사용하여 테스트 실행
    # 인메모리 데이터베이스를 사용하므로 테스트 후 자동으로 롤백됩니다.
    try:
        yield async_session
    finally:
        await async_session.close()
        app.dependency_overrides.pop(get_async_db, None)


# User 객체를 생성하는 fixture
@pytest_asyncio.fixture
async def user_fixture(db_session: AsyncSession) -> User:
    """
    테스트용 사용자 객체를 생성합니다.
    기본값을 사용하거나, 원하는 값으로 생성할 수 있습니다.
    """
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    hashed_password = "hashed_password"
    created_user = await create_user(
        db=db_session, user_in=user_in, hashed_password=hashed_password
    )

    return created_user
