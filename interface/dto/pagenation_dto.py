from typing import Annotated

from fastapi import Query, status, HTTPException
from pydantic import BaseModel, model_validator


class PagenationRequestParams(BaseModel):
    max_count: Annotated[
        int | None,
        Query(
            default=None,
            description="페이지네이션 결과에 담길 객체의 최대 개수",
        ),
    ]
    start_offset: Annotated[
        int | None,
        Query(
            default=None,
            description="페이지네이션 기준이 되는 오프셋. 오프셋 1부터 시작하며 이 위치의 객체가 시간상 가장 오래된 객체를 의미",
        ),
    ]

    @model_validator(mode="after")
    def validate_all_or_none(cls, model):
        try:
            if model.max_count is None and model.start_offset is not None:
                raise ValueError(
                    "start_offset 은 max_count 가 None 인 상황에서 지정될 수 없습니다."
                )
            if model.max_count is not None and model.max_count < 1:
                raise ValueError("max_count 는 None 이거나 1 이상이어야 합니다")
            if model.start_offset is not None and model.start_offset < 1:
                raise ValueError("start_offset 은 None 이거나 1 이상이어야 합니다")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return model

    def is_paginated(self) -> bool:
        return self.max_count is not None
