from fastapi import HTTPException, status


class InvalidToken(HTTPException):
    def __init__(self, detail: str = "유효하지 않은 토큰입니다."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ExpiredToken(HTTPException):
    def __init__(self, detail: str = "Token이 만료되었습니다."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )
