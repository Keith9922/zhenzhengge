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
    cors_origins: list[str] = Field(default_factory=lambda: [
        "http://localhost:3000", "http://localhost:3006",
        "http://127.0.0.1:3000", "http://127.0.0.1:3006",
    ])
    cors_origin_regex: str = (
        r"^chrome-extension://.*$|"
        r"^http://localhost:(3000|3001|3006)$|"
        r"^http://127\.0\.0\.1:(3000|3001|3006)$"
    )
    service_tag: str = "zhenzhengge-api"
    enable_demo_seed: bool = False
    require_auth: bool = True
    auth_tokens: str = "dev-admin-token:admin,dev-operator-token:operator,dev-viewer-token:viewer"
    extension_api_token: str = ""
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
    monitor_scheduler_enabled: bool = True
    monitor_scheduler_interval_seconds: int = 30
    capture_allow_http_fallback: bool = True
    draft_generation_strict: bool = True
    evidence_timestamp_enabled: bool = False
    evidence_timestamp_tsa_url: str = ""
    evidence_timestamp_timeout_seconds: int = 15
    evidence_timestamp_required: bool = False
    harness_agent_enabled: bool = False
    harness_cli_command: str = "hermes"
    harness_provider: str = "auto"
    harness_model: str = ""
    harness_toolsets: str = "skills,memory"
    harness_skills: str = "hermes-agent,wps-word"
    harness_timeout_seconds: int = 120

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
