from fastapi import FastAPI

# from src.users.router import router as users_router
# from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.app_name,
    description="낯가리는 사람들 API",
    version="0.1.0",
    debug=settings.debug_mode,
)

# origins = [
#     "http://localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # 특정 출처만 허용
#     allow_credentials=True,  # 쿠키를 포함한 요청 허용
#     allow_methods=["*"],  # 모든 HTTP 메소드 허용 (GET, POST, PUT, DELETE 등)
#     allow_headers=["*"],  # 모든 HTTP 헤더 허용
# )

# 라우터 등록
# API_V1_PREFIX = "/api/v1"

# app.include_router(users_router, prefix="{API_V1_PREFIX}/users", tags=["Users"])


@app.get("/")
async def root():
    """
    루트 엔드포인트입니다. 간단한 메시지를 반환합니다.
    """
    return {"message": "낯가리는 사람들 API"}


@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트입니다. 애플리케이션이 정상 작동 중인지 확인합니다.
    모니터링 / 로드 밸런싱에 사용될 수 있습니다.
    """
    return {
        "status": "ok",
        "database_url": settings.database_url.split("://")[0]
        + "://***",  # 보안상 일부만 표시
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        reload_dirs=["src"],
        log_level="debug" if settings.debug_mode else "info",
    )
