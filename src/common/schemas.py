from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    """
    애플리케이션 전반에서 사용될 Pydantic 모델의 기본 설정을 정의합니다.
    - str_strip_whitespace: 문자열 필드의 앞뒤 공백을 자동으로 제거합니다.
    - validate_assignment: 생성된 모델 인스턴스의 필드에 값을 할당할 때 유효성 검사를 다시 수행합니다.
    - extra="forbid": 스키마에 정의되지 않은 필드가 입력으로 들어오면 에러를 발생시킵니다.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )


# 만약 페이지네이션 응답과 같이 다른 곳에서도 공통으로 쓰일 스키마가 있다면
# 이곳에 추가할 수 있습니다.
# class PaginatedResponse(BaseModel):
#     total: int
#     items: list
