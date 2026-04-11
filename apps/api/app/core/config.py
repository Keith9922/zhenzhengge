from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "证证鸽 API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    enable_docs: bool = True
    database_url: str = "sqlite:///./data/zhenzhengge.db"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3006", "http://127.0.0.1:3006"])
    cors_origin_regex: str = (
        r"^chrome-extension://.*$|"
        r"^http://localhost:(3000|3001|3006)$|"
        r"^http://127\.0\.0\.1:(3000|3001|3006)$"
    )
    service_tag: str = "zhenzhengge-api"
    enable_demo_seed: bool = True
    llm_provider: str = "stub"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = Field(default="", repr=False)
    llm_model: str = "mimo-v2-pro"
    llm_reasoning_model: str = "o1-mini"
    llm_tts_model: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

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
