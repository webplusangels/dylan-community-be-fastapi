from pydantic import field_validator
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

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    def validate_access_token_expire(cls, v):
        """
        액세스 토큰 만료 시간을 검증합니다.
        1분 이상, 1440분(24시간) 이하이어야 합니다.
        """
        if v <= 0 or v > 1440:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 1440")
        return v

    @field_validator("REFRESH_TOKEN_EXPIRE_MINUTES")
    def validate_refresh_token_expire(cls, v):
        """
        리프레시 토큰 만료 시간을 검증합니다.
        1분 이상, 43200분(30일) 이하이어야 합니다.
        """
        if v <= 0 or v > 43200:
            raise ValueError("REFRESH_TOKEN_EXPIRE_MINUTES must be between 1 and 43200")
        return v


# 애플리케이션 설정 인스턴스 생성
settings = Settings()
