from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # ollama envs
    ollama_base_url: str = 'http://ollama:11434'
    ollama_model: str = 'qwen3:4b'

    # smtp envs
    smtp_host: str = 'mailhog'
    smtp_port: int = 1025

    # email envs
    email_from: str = 'info@wskz.pl'


@lru_cache
def get_settings() -> Settings:
    return Settings()
