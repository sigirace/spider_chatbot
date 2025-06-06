from pydantic import BaseModel, Field


class TranslationParameters(BaseModel):
    """
    번역 체인에 사용할 패러미터 파싱용 클래스
    번역할 문장과 함께, 번역 대상 언어에 대한 내용을 담는다.
    """

    string_to_translate: str = Field(..., description="번역을 수행할 전체 문장")
    target_language: str = Field(..., description="번역 대상 언어")
