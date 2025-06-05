class FileServiceError(Exception):
    def __init__(self, detail: str):
        self.message = f"파일 작업 중 에러 발생: {detail}"
        super().__init__(self.message)
