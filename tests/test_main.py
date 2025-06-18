# tests/test_main.py
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.core.config import settings

# --- Helper functions ---


def check_root_response(data):
    assert data == {"message": "낯가리는 사람들 API"}


def check_health_response(data):
    assert data["status"] == "ok"
    assert "database_url" in data
    assert "://***" in data["database_url"]


# --- Tests ---


def test_root_endpoint_sync(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    check_root_response(response.json())


@pytest.mark.asyncio
async def test_root_endpoint_async(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    check_root_response(response.json())


def test_health_check_sync(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    check_health_response(response.json())


@pytest.mark.asyncio
async def test_health_check_async(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    check_health_response(response.json())


@pytest.mark.asyncio
async def test_database_url_security(async_client: AsyncClient):
    """데이터베이스 URL 보안 테스트 - 민감한 정보 노출 방지"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()

    db_url = data["database_url"]

    # URL 구조 검증
    parsed_url = urlparse(db_url)
    assert parsed_url.scheme in [
        "sqlite+aiosqlite",
        # "mysql+pymysql", # 현재는 지원하지 않음
        # "postgresql+asyncpg", # 현재는 지원하지 않음
    ]
    assert "***" in db_url, "URL 마스킹이 적용되지 않음"

    sensitive_patterns = [
        "password",
        "pwd",
        "secret",
        "key",
        "admin",
        "root",
        "user",
        "username",
        "@localhost",
        "@127.0.0.1",
        "@192.168",
    ]
    for pattern in sensitive_patterns:
        assert pattern not in db_url.lower(), f"민감한 정보 '{pattern}'가 URL에 노출됨"


@pytest.mark.asyncio
async def test_health_check_database_type_extraction(async_client: AsyncClient):
    """헬스체크에서 데이터베이스 타입 추출 테스트"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()

    db_url = data["database_url"]
    if "://" in db_url:
        extracted_type = db_url.split("://")[0]
        if settings.DATABASE_URL:
            expected_type = settings.DATABASE_URL.split("://")[0]
            assert (
                extracted_type == expected_type
            ), f"예상 DB 타입 '{expected_type}'과 응답 DB 타입 '{extracted_type}'이 다릅니다."


@pytest.mark.asyncio
async def test_health_check_response_format(async_client: AsyncClient):
    """헬스체크 응답 형식 검증"""
    response = await async_client.get("/health")
    assert response.status_code == 200

    data = response.json()

    # 필수 필드 존재 확인
    required_fields = ["status", "database_url"]
    for field in required_fields:
        assert field in data, f"응답에 필수 필드 '{field}'가 없음"

    # 응답 타입 검증
    assert isinstance(data["status"], str), "status는 문자열이어야 함"
    assert isinstance(data["database_url"], str), "database_url은 문자열이어야 함"

    # status 값 검증
    assert data["status"] == "ok", "헬스체크 상태가 'ok'가 아님"


def test_nonexistent_endpoint_sync(client: TestClient):
    """존재하지 않는 엔드포인트 테스트 (동기)"""
    response = client.get("/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_nonexistent_endpoint_async(async_client: AsyncClient):
    """존재하지 않는 엔드포인트 테스트 (비동기)"""
    response = await async_client.get("/nonexistent")
    assert response.status_code == 404


def test_root_endpoint_methods(client: TestClient):
    """루트 엔드포인트 HTTP 메서드 테스트"""
    # GET은 허용
    response = client.get("/")
    assert response.status_code == 200

    # POST는 허용되지 않음
    response = client.post("/")
    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.parametrize(
    "endpoint,expected_status",
    [
        ("/", 200),
        ("/health", 200),
        ("/nonexistent", 404),
        ("/api/v1/nonexistent", 404),
    ],
)
def test_endpoints_status_codes(
    client: TestClient, endpoint: str, expected_status: int
):
    """엔드포인트별 상태 코드 테스트"""
    response = client.get(endpoint)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_health_check_when_db_unavailable():
    """데이터베이스 연결 실패 시 헬스체크 동작 (확장)"""
    # TODO: 데이터베이스 연결이 불가능한 상황을 시뮬레이션하고,
    # /health 엔드포인트가 적절한 오류 응답을 반환하는지 테스트합니다.
    # 향후 실제 DB 연결 시 필요하면 이 테스트를 구현할 수 있습니다.
    pass
