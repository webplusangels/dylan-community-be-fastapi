from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    """

    # DB 설정
    DATABASE_URL: str  # 예: "mysql+asyncmy://user:password@host/db"

    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # 애플리케이션 설정
    APP_NAME: str = "낯가리는 사람들"
    DEBUG_MODE: bool = False

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="forbid",  # 추가 설정 비허용
    )


# 애플리케이션 설정 인스턴스 생성
settings = Settings()
