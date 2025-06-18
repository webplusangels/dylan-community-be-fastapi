from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """
    JWT 토큰을 표현하는 모델
    """

    access_token: str = Field(
        ...,
        description="JWT 액세스 토큰",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field("bearer", description="토큰 타입", examples=["bearer"])
    refresh_token: str = Field(
        ...,
        description="JWT 리프레시 토큰 (선택적)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    model_config = ConfigDict(
        validate_assignment=True,  # 할당 시 유효성 검사
        extra="forbid",  # 정의되지 않은 필드는 허용하지 않음
    )


class TokenData(BaseModel):
    """
    JWT 토큰에서 사용자 정보를 추출하기 위한 모델
    """

    user_id: str = Field(
        ...,
        description="사용자 고유 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    roles: str | None = Field(
        None,
        description="사용자 역할 (예: 'user', 'admin')",
        examples=["user", "admin"],
    )

    model_config = ConfigDict(
        validate_assignment=True,  # 할당 시 유효성 검사
        extra="forbid",  # 정의되지 않은 필드는 허용하지 않음
    )
