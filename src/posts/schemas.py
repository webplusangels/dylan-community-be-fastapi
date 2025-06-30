from datetime import datetime

from pydantic import ConfigDict, Field

from src.common.schemas import AppBaseModel
from src.users.schemas import UserProfilePublic


class PostBase(AppBaseModel):
    """
    게시글의 기본 속성을 정의하는 모델
    다른 스키마들이 상속받아 사용할 수 있는 클래스
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=25,
        description="게시글 제목 (1-25자)",
        examples=["첫 번째 게시글", "FastAPI 시작하기", "Dylan 커뮤니티 소개"],
    )
    content: str = Field(
        ...,
        min_length=1,
        description="게시글 내용",
        examples=[
            "이것은 첫 번째 게시글의 내용입니다.",
            "FastAPI를 사용하여 웹 애플리케이션을 개발하는 방법에 대해 설명합니다.",
            "Dylan 커뮤니티는 개발자들이 모여 지식을 공유하는 공간입니다.",
        ],
    )
    image_path: str | None = Field(
        None,
        max_length=255,
        description="게시글 이미지 URL",
        examples=[
            "https://example.com/images/post1.jpg",
            "https://example.com/images/post2.png",
        ],
    )


class PostCreate(PostBase):
    """
    게시글 생성을 위한 스키마
    PostBase를 상속받아 추가적인 필드를 정의
    """

    user_id: str = Field(
        ...,
        description="게시글 작성자의 사용자 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class PostUpdate(AppBaseModel):
    """
    게시글 업데이트를 위한 스키마
    PostBase를 상속받아 업데이트 가능한 필드를 정의
    """

    title: str | None = Field(
        None,
        min_length=1,
        max_length=25,
        description="게시글 제목 (1-25자)",
        examples=["업데이트된 게시글 제목", "FastAPI 고급 기능"],
    )
    content: str | None = Field(
        None,
        min_length=1,
        description="게시글 내용",
        examples=["업데이트된 게시글 내용입니다."],
    )
    image_path: str | None = Field(
        None,
        max_length=255,
        description="게시글 이미지 URL",
        examples=["https://example.com/images/updated_post.jpg"],
    )


class PostRead(PostBase):
    """
    게시글 정보를 읽기 위한 스키마
    PostBase를 상속받고, DB에서 자동 생성되는 필드를 추가로 정의
    """

    id: str = Field(
        ...,
        description="게시글 고유 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    user_id: str = Field(
        ...,
        description="게시글 작성자의 사용자 ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    views: int = Field(
        default=0,
        description="게시글 조회수 (음수가 될 수 없음)",
        examples=[0, 10, 100],
    )
    likes: int = Field(
        default=0,
        description="게시글 좋아요 수 (음수가 될 수 없음)",
        examples=[0, 5, 20],
    )
    comments_count: int = Field(
        default=0,
        description="게시글 댓글 수 (음수가 될 수 없음)",
        examples=[0, 2, 15],
    )
    created_at: datetime = Field(
        ...,
        description="게시글 정보 생성 시간 (ISO 8601 형식)",
        examples=["2023-10-01T12:00:00Z"],
    )
    updated_at: datetime = Field(
        ...,
        description="게시글 정보 업데이트 시간 (ISO 8601 형식)",
        examples=["2023-10-01T12:00:00Z"],
    )

    author: UserProfilePublic = Field(
        ...,
        description="게시글 작성자의 공개 프로필 정보",
        examples=[
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "dylan_dev",
                "profile_image_path": "https://example.com/images/profile.jpg",
            }
        ],
    )

    model_config = ConfigDict(
        from_attributes=True,  # 속성에서 모델로 변환 가능
    )


class PostList(AppBaseModel):
    """
    게시글 목록을 표현하는 모델
    여러 개의 게시글 정보를 포함하는 리스트 형태로 정의
    """

    posts: list[PostRead] = Field(
        ...,
        description="게시글 정보 리스트",
        examples=[
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "첫 번째 게시글",
                "content": "이것은 첫 번째 게시글의 내용입니다.",
                "image_path": "https://example.com/images/post1.jpg",
                "views": 10,
                "likes": 5,
                "comments_count": 2,
                "created_at": "2023-10-01T12:00:00Z",
                "updated_at": "2023-10-01T12:00:00Z",
                "author": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "dylan_dev",
                    "profile_image_path": "https://example.com/images/profile.jpg",
                },
            }
        ],
    )

    model_config = ConfigDict(
        from_attributes=True,  # 속성에서 모델로 변환 가능
    )


class PostListResponse(AppBaseModel):
    """
    게시글 목록 응답을 표현하는 모델
    게시글 목록과 함께 페이지네이션 정보를 포함
    """

    posts: list[PostRead] = Field(
        ...,
        description="게시글 정보 리스트",
    )
    total_count: int = Field(
        description="전체 게시글 수",
        examples=[100, 250],
    )
    page: int = Field(
        description="현재 페이지 번호",
        examples=[1, 2, 3],
    )
    page_size: int = Field(
        description="페이지당 게시글 수",
        examples=[10, 20, 50],
    )
    has_next: bool = Field(
        ...,
        description="다음 페이지가 있는지 여부",
        examples=[True, False],
    )

    model_config = ConfigDict(
        from_attributes=True,  # 속성에서 모델로 변환 가능
    )
