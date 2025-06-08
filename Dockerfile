### 1단계: 빌드 스테이지 ###
FROM python:3.11-slim AS builder

# 필수 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# requirements 설치
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
WORKDIR /app
COPY . .

# .env.docker → .env 로 복사 (빌드 시점에만)
RUN cp .env.docker .env

### 2단계: 실행 스테이지 ###
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1단계에서 설치한 패키지와 코드 복사
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "debug", \
     "--lifespan", "on"]