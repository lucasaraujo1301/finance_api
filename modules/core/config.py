from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", frozen=True)

    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_DRIVER: str
    DATABASE_TEST_NAME: str
    DATABASE_TEST_PORT: int = 5433

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

    @property
    def database_test_url(self) -> URL:
        return URL.create(
            drivername=self.DATABASE_DRIVER,
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_TEST_PORT,
            database=self.DATABASE_TEST_NAME,
        )


settings = Settings()  # ty: ignore
