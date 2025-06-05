from datetime import UTC, datetime, timedelta
from fastapi import HTTPException, status
from config import get_settings
from jose import JWTError, jwt

settings = get_settings()

jwt_config = settings.jwt

ALGORITHM = jwt_config.jwt_algorithm
SECRET_KEY = jwt_config.jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config.access_token_expires_in
REFRESH_TOKEN_EXPIRES_IN = jwt_config.refresh_token_expires_in


def create_access_token(payload: dict) -> str:
    try:
        payload = payload.copy()
        payload["exp"] = datetime.now(UTC) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return access_token
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


def create_refresh_token(payload: dict) -> str:
    try:
        payload = payload.copy()
        payload.update(
            {
                "exp": datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRES_IN),
                "type": "refresh_token",
            }
        )
        refresh_token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return refresh_token
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


def decode_token(token: str) -> dict:
    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return decoded
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


def decode_refresh_token(token: str) -> dict:
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh_token":
            raise HTTPException(
                status_code=401,
                detail="Not a refresh token.",
            )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
