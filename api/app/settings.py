from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env_exemple', env_file_encoding='utf-8'
    )
    DATABASE_URL: str
