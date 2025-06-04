from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    """

    # DB 설정
    database_url: str  # 예: "mysql+asyncmy://user:password@host/db"

    # JWT 설정
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 애플리케이션 설정
    app_name: str = "낯가리는 사람들"
    debug_mode: bool = False

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="forbid",  # 추가 설정 비허용
    )


# 애플리케이션 설정 인스턴스 생성
settings = Settings()
