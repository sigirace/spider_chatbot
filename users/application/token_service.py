from fastapi import HTTPException, status
from users.domain.model.user import AuthToken
from utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    decode_refresh_token,
)


class TokenService:

    def publish_token(self, user_id: str) -> AuthToken:
        """
        AccessToken + RefreshToken을 발급한다.
        """
        payload = {
            "user_id": user_id,
        }

        access_token = create_access_token(payload=payload)
        refresh_token = create_refresh_token(payload=payload)

        return AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def validate_token(self, access_token: str) -> bool:
        try:
            decoded = decode_token(access_token)

            if "user_id" not in decoded:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )

            return True

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresh Token을 검증하고, 새로운 Access Token을 발급한다.
        """
        try:
            decoded = decode_refresh_token(refresh_token)

            payload = {
                "user_id": decoded["user_id"],
            }

            new_access_token = create_access_token(payload=payload)

            return new_access_token

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
