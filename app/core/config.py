from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy import URL

type LogLevel = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_user: str = "admin"
    postgres_password: SecretStr = SecretStr("admin")
    postgres_db: str = "deribit"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    redis_url: str = "redis://localhost:6379/0"

    deribit_base_url: str = "https://www.deribit.com/api/v2"
    deribit_timeout_seconds: float = Field(default=10, gt=0)

    tickers: Annotated[tuple[str, ...], NoDecode] = Field(
        default=("btc_usd", "eth_usd"), min_length=1
    )
    collect_interval_seconds: float = Field(default=60, gt=0)

    log_level: LogLevel = "INFO"

    @field_validator("tickers", mode="before")
    @classmethod
    def split_tickers(cls, value: object) -> object:
        if isinstance(value, str):
            return tuple(item.strip().lower() for item in value.split(",") if item.strip())
        return value

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
