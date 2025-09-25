from typing import Set, Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
from datetime import timedelta

class Settings(BaseSettings):
    # Logging
    log_level: str = Field()
    log_dir: Path = Field()
    log_file: str = Field()

    # Security
    secret_key: str = Field(default="fallback-secret-key")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=7)

    # Database
    db_user: str = Field()
    db_pwd: str = Field()
    db_host: str = Field()
    db_port: int = Field()
    db_name: str = Field()

    # api_limit
    register_limit_per_hour: int = Field()

    # masking fields
    masking_keys: str = Field()

    @property
    def masking_keys_set(self) -> Set[str]:
        return set(s.strip() for s in self.masking_keys.split("") if s.strip())

    @property
    def db_url(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(days=self.refresh_token_expire_days)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding = "utf-8"
    )

# Instantiate settings to use everywhere
settings = Settings()
