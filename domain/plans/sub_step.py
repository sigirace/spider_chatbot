from typing import Literal, Optional
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

# from pydantic import field_validator

from domain.plans.observation_item import ObservationItem


class SubStepInfo(BaseModel):
    """
    하나의 서브 스텝을 표현하기 위한 규격
    """

    model_config = ConfigDict(
        validate_assignment=True
    )  # 속성 대입시에도 검증하도록 하는 설정

    # 내부 변수
    status: Annotated[
        Literal["pending", "processing", "complete", "stalled"],
        Field(default="pending", description="이 서브 스텝의 실행 상태"),
    ] = "pending"
    title: Annotated[str, Field(default="", description="서브 스텝을 표현하는 문자열")]
    observation: Annotated[
        Optional[ObservationItem], Field(description="서브 스텝 실행의 결과")
    ] = None

    # # 필드 검증 예시: title 에 대한 검증
    # @field_validator("title")
    # @classmethod
    # def validate_title(cls, new_value:str) -> str:
    #     MAX_LEN = 255
    #     if len(new_value) > MAX_LEN:
    #         raise ValueError(f"title은 최대 {MAX_LEN}자까지만 가능합니다.")
    #     return new_value

    # """
    # 더 복잡한 검증 로직이 필요하다면 pydantic의 model_validator 의 적용도 고려 가능
    # """
    # pass
