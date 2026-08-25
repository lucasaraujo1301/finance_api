from pydantic_settings import BaseSettings, SettingsConfigDict


class UserSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", frozen=True, extra="ignore")

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_PASSWORD_UPDATE_TOKEN_EXPIRE_MINUTES: int = 15


user_settings = UserSettings()  # ty: ignore
