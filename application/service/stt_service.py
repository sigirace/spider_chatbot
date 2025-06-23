import base64
from pydub import AudioSegment
from io import BytesIO

from fastapi import HTTPException
from domain.api.ml_repository import IMLRepository
from domain.api.models import STTResponse


class STTService:
    def __init__(
        self,
        ml_repository: IMLRepository,
    ):
        self.expected_rate = 16000
        self.ml_repository = ml_repository

    def load_and_resample_audio(self, audio_file_path: str) -> AudioSegment:
        """오디오 파일을 불러오고 샘플레이트가 다르면 16kHz로 변환"""
        try:
            sound = AudioSegment.from_file(audio_file_path)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="오디오 파일을 읽을 수 없습니다.",
            )

        if sound.frame_rate != self.expected_rate:
            sound = sound.set_frame_rate(self.expected_rate)
        return sound

    def encode_audio_to_base64(self, audio: AudioSegment) -> str:
        """AudioSegment 객체를 base64로 인코딩"""
        buffer = BytesIO()
        audio.export(buffer, format="wav")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return encoded

    async def transcribe(self, audio_file_path: str) -> STTResponse:
        """
        오디오 파일을 읽고 샘플레이트를 16k로 맞춰 인코딩한 후 전송
        """
        audio = self.load_and_resample_audio(audio_file_path)
        encoded_audio = self.encode_audio_to_base64(audio)
        return await self.ml_repository.stt(encoded_audio)
