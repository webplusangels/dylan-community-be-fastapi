from passlib.context import CryptContext

# 암호화 해싱 알고리즘과 정책 정의
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    주어진 비밀번호를 해싱합니다.

    :param password: 해싱할 비밀번호
    :return: 해싱된 비밀번호
    """
    if not password:
        raise ValueError("빈 문자열은 비밀번호로 사용할 수 없습니다.")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    주어진 평문 비밀번호와 해싱된 비밀번호를 비교해 일치 여부를 반환합니다
    :param plain_password: 평문 비밀번호
    :param hashed_password: 해싱된 비밀번호
    :return: 비밀번호가 일치하면 True, 그렇지 않으면 False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False
