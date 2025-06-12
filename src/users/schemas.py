from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.common.schemas import AppBaseModel


def validate_password(value: str) -> str:
    """
    비밀번호 유효성 검사 함수
    영문 대소문자, 숫자 조합을 요구
    """
    if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError("비밀번호는 영문과 숫자를 포함해야 합니다.")
    return value


class UserBase(AppBaseModel):
    """
    사용자의 기본 속성을 정의하는 모델
    다른 스키마들이 상속받아 사용할 수 있는 클래스
    """

    email: EmailStr = Field(
        ...,
        description="사용자 이메일 주소",
        examples=["test@example.com", "user1@domain.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="사용자명 (3-50자, 영문 대소문자, 숫자, 밑줄(_)만 허용)",
        examples=["user123", "test_user", "example_user"],
    )
    profile_image_path: AnyHttpUrl | None = Field(
        None,
        max_length=255,
        description="프로필 이미지 URL",
        examples=[
            "https://example.com/images/profile.jpg",
            "https://example.com/images/avatar.png",
        ],
    )


class UserCreate(UserBase):
    """
    사용자 생성을 위한 스키마
    UserBase를 상속받아 추가적인 필드를 정의
    """

    # 서비스 계층에서 평문 비밀번호를 받기 위한 필드
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="사용자 비밀번호 (8-128자)",
        examples=["password123", "securePassword!@#1234"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password(value)


class UserUpdate(AppBaseModel):
    """
    사용자 업데이트를 위한 스키마
    UserBase를 상속받아 일부 필드를 선택적으로 업데이트할 수 있도록 정의
    """

    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="사용자명 (3-50자, 영문 대소문자, 숫자, 밑줄(_)만 허용)",
        examples=["new_user123", "updated_user"],
    )
    profile_image_path: AnyHttpUrl | None = Field(
        None,
        max_length=255,
        description="프로필 이미지 URL",
        examples=[
            "https://example.com/images/new_profile.jpg",
            "https://example.com/images/new_avatar.png",
        ],
    )


class UserUpdatePassword(AppBaseModel):
    """
    사용자 비밀번호 업데이트를 위한 스키마
    기존 비밀번호와 새 비밀번호를 받기 위한 모델
    """

    current_password: str = Field(
        ...,
        description="현재 비밀번호 (8-128자)",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="새 비밀번호 (8-128자)",
        examples=["newPassword123", "NewSecure!@#789"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return validate_password(value)


class UserRead(UserBase):
    """
    사용자 정보를 읽기 위한, API 응답을 위한 스키마
    UserBase를 상속받고, DB에서 자동 생성되는 필드를 추가로 정의
    """

    id: str = Field(
        ...,
        description="사용자 고유 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    is_active: bool = Field(
        ...,
        description="사용자 활성화 상태",
        examples=[True, False],
    )
    created_at: datetime = Field(
        ...,
        description="사용자 생성 시간 (ISO 8601 형식)",
        examples=["2023-10-01T12:00:00Z"],
    )
    updated_at: datetime = Field(
        ...,
        description="사용자 정보 업데이트 시간 (ISO 8601 형식)",
        examples=["2023-10-01T12:00:00Z"],
    )

    model_config = ConfigDict(
        from_attributes=True,  # 속성에서 모델로 변환 가능
        validate_assignment=False,  # 명시적으로 False로 오버라이드
    )


class UserProfile(BaseModel):
    """
    사용자 프로필 정보를 표현하는 모델
    공개용으로 사용되는 사용자 정보를 포함해 API 응답에 사용
    """

    username: str = Field(..., description="사용자명")
    profile_image_path: AnyHttpUrl | None = Field(None, description="프로필 이미지 URL")

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class UserInDB(UserRead):
    """
    내부 데이터베이스에서 사용자 정보를 읽기 위한 스키마
    UserRead를 상속받아 DB에서 사용하는 필드를 추가로 정의
    """

    hashed_password: str = Field(
        ...,
        description="해시된 사용자 비밀번호",
        examples=["$2b$12$eImiTMZG4TQ1mZ9j5a5eOe"],
    )


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
