from typing import Literal, Annotated

from pydantic import BaseModel, Field


class ControlSignal(BaseModel):
    control_signal: Annotated[
        Literal[
            # "final_answer_stream_start",
            # "final_answer_stream_end",
            "title_generation_complete",
            "error_occurred",
            "stt_completed",
            "primary_page",
        ],
        Field(description="제어 신호"),
    ]

    detail: Annotated[
        str | None,
        Field(description="상세 정보"),
    ] = None


# class FinalAnswerControlSignal(ControlSignal):
#     control_signal: Literal[  # type: ignore
#         "final_answer_stream_start",
#         "final_answer_stream_end",
#     ] = Field(..., description="최종 응답 제어 신호")


# class TitleGenerationCompleteSignal(ControlSignal):
#     control_signal: str = Field(  # type: ignore
#         "title_generation_complete", description="최종 응답 제어 신호"
#     )
