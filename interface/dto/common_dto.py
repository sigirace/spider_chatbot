from pydantic import BaseModel, Field


class DeletedResponse(BaseModel):
    """
    삭제된 객체에 대한 수행 메세지 전달
    """

    id: str = Field(..., description="삭제된 객체의 ID")
    success: bool = Field(default=True, description="삭제 성공 여부")
    message: str = Field(default="삭제가 완료되었습니다.", description="결과 메시지")
    status_code: int = Field(default=200, description="HTTP 상태 코드")
