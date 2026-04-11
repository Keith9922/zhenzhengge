from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "证证鸽 API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    enable_docs: bool = True
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    cors_origin_regex: str = r"^chrome-extension://.*$|^http://localhost:(3000|3001)$|^http://127\.0\.0\.1:(3000|3001)$"
    service_tag: str = "zhenzhengge-api"

    model_config = SettingsConfigDict(
        env_prefix="ZHZG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
