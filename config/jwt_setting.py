from config.setting import BaseAppSettings


class JWTSetting(BaseAppSettings):
    jwt_algorithm: str
    jwt_secret_key: str
    access_token_expires_in: int
    refresh_token_expires_in: int
