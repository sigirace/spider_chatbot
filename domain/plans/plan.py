from typing import Literal
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict
from domain.plans.step import StepList

# from pydantic import field_validator


class PlanInfo(BaseModel):
    """
    LLM이 생성한 문제 해결 단계를 파싱하기 위한 클래스
    StepInfo 가 문제 해결을 위한 각 수행 단계를 의미하며, 전체 과정은 이 단계들을 순서대로 담은 리스트다
    """

    model_config = ConfigDict(
        validate_assignment=True
    )  # 속성 대입시에도 검증하도록 하는 설정

    status: Annotated[
        Literal["pending", "processing", "complete", "stalled"],
        Field(default="pending", description="이 서브 스텝의 실행 상태"),
    ] = "pending"
    step_list: Annotated[
        StepList, Field(description="사용자의 요청에 대한 수행 계획", default=[])
    ] = StepList()
