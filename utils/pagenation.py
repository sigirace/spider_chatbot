from interface.dto.pagenation_dto import PagenationRequestParams


def need_pagenation(params: PagenationRequestParams):
    """
    기본적인 값 검증은 모델의 DTO에서 수행하므로 간단하게 구현
    """
    return params.max_count is not None
