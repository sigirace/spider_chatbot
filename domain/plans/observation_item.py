from typing import Literal, Any
from typing import Annotated, Union
from pydantic import BaseModel, Field, ConfigDict

# from pydantic import field_validator


class ObservationItem(BaseModel):
    """
    서브 스텝은 수행 결과를 리스트 형식으로 가질 수 있음.
    이 클래스는 수행 결과 리스트에 들어가는 아이템의 규격
    """

    model_config = ConfigDict(
        validate_assignment=True
    )  # 속성 대입시에도 검증하도록 하는 설정

    # 내부 변수
    type: Annotated[
        Literal["string", "key_value", "list", "keyword"],
        Field(
            ...,
            description="프론트엔드에서 value를 출력할 형태를 결정하기 위한 타입 명칭",
        ),
    ]
    value: Annotated[
        Union[str, dict[str, Any], list[Any]],
        Field(..., description="수행 결과 관측된 값"),
    ]
