class ExternalApiError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class LlmServiceError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)
