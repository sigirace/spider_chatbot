from typing import Literal, Optional
from typing import Annotated
from pydantic import RootModel, BaseModel, Field, ConfigDict

# from pydantic import field_validator

from domain.plans.sub_step import SubStepInfo
from domain.plans.observation_item import ObservationItem


class StepInfo(BaseModel):
    """
    하나의 스텝을 표현하기 위한 규격
    """

    model_config = ConfigDict(
        validate_assignment=True
    )  # 속성 대입시에도 검증하도록 하는 설정

    # 내부 변수
    status: Annotated[
        Literal["pending", "processing", "complete", "stalled"],
        Field(default="pending", description="이 서브 스텝의 실행 상태"),
    ] = "pending"
    agent: Annotated[
        str, Field(default="", description="스텝에서 사용할 에이전트의 이름")
    ]
    thought: Annotated[str, Field(default="", description="이 스텝에 대한 세부 정보")]
    sub_step_list: Annotated[
        list[SubStepInfo], Field(description="이 스텝이 가지는 서브 스텝의 리스트")
    ] = []
    observation: Annotated[
        Optional[ObservationItem],
        Field(description="서브 스텝 실행의 결과를 종합하여 만든 하나의 대표 출력"),
    ] = None

    # # 필드 검증 예시: title 에 대한 검증
    # @field_validator("title")
    # @classmethod
    # def validate_title(cls, new_value:str) -> str:
    #     MAX_LEN = 255
    #     if len(new_value) > MAX_LEN:
    #         raise ValueError(f"title은 최대 {MAX_LEN}자까지만 가능합니다.")
    #     return new_value

    """
    더 복잡한 검증 로직이 필요하다면 pydantic의 model_validator 의 적용도 고려 가능
    """
    pass


class StepList(RootModel[list[StepInfo]]):
    """
    LLM이 생성한 문제 해결 단계를 파싱하기 위한 클래스
    내부에서 정의하는 SolvingStep 이 문제 해결 단계를 의미하며, 전체 과정은 이 단계들을 순서대로 담은 리스트다

    이 객체의 인스턴스를 enumerate 등으로 리스트로써 접근해야 하는 경우, StepList.model_dump() 등으로 접근할 것.
    (__iter__ 등의 오버라이드 등으로 해결 가능하나, BaseModel 과의 호환성을 잃을 수 있음)
    """

    model_config = ConfigDict(
        validate_assignment=True
    )  # 속성 대입시에도 검증하도록 하는 설정
    root: Annotated[
        list[StepInfo], Field(description="사용자의 요청에 대한 수행 계획", default=[])
    ] = []

    def __getitem__(self, index: int) -> StepInfo:
        return self.root[index]

    def __setitem__(self, index: int, value: StepInfo) -> None:
        self.root[index] = value

    def __len__(self) -> int:
        return len(self.root)

    def append(self, item: StepInfo) -> None:
        self.root.append(item)

    def extend(self, items: list[StepInfo]) -> None:
        self.root.extend(items)

    def insert(self, index: int, item: StepInfo) -> None:
        self.root.insert(index, item)

    def __repr__(self) -> str:
        return repr(self.root)

    def __str__(self) -> str:
        return str(self.root)
