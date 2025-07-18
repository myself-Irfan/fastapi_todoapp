from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from datetime import timedelta

class Settings(BaseSettings):
    # Logging
    log_dir: Path = Field()
    log_file: str = Field()

    # Security
    secret_key: str = Field(default="fallback-secret-key")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=7)

    # Database
    db_url: str

    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(days=self.refresh_token_expire_days)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate settings to use everywhere
settings = Settings()
