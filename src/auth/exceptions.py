from fastapi import HTTPException, status


class TokenError(HTTPException):
    """토큰 관련 기본 예외"""

    pass


class TokenExpiredError(TokenError):
    """토큰 만료 예외"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenBlockedError(TokenError):
    """토큰 블락리스트 예외"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용이 금지된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(TokenError):
    """잘못된 토큰 예외"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
