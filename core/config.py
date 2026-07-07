from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_DRIVER: str

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername=self.DATABASE_DRIVER,
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # ty: ignore
