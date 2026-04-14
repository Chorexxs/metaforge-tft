from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    riot__api_key: str = Field(default="", validation_alias="RIOT_API_KEY")

    insforge__url: str = Field(
        default="https://36b6whsc.eu-central.insforge.app",
        validation_alias="INSFORGE_URL",
    )

    insforge__api_key: str = Field(
        default="",
        validation_alias="INSFORGE_API_KEY",
    )

    tft__set_version: int = Field(default=14, validation_alias="TFT_SET_VERSION")

    patch_check_interval_hours: int = Field(
        default=6, validation_alias="PATCH_CHECK_INTERVAL_HOURS"
    )

    app__host: str = Field(default="127.0.0.1", validation_alias="APP_HOST")

    app__port: int = Field(default=8000, validation_alias="APP_PORT")

    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    discord__webhook_url: str | None = Field(default=None, validation_alias="DISCORD_WEBHOOK_URL")

    live_client__url: str = Field(
        default="https://127.0.0.1:2999/liveclientdata/",
        validation_alias="LIVE_CLIENT_URL",
    )

    live_client__poll_interval_seconds: int = Field(
        default=5, validation_alias="LIVE_CLIENT_POLL_INTERVAL_SECONDS"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
