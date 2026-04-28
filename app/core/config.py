from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore', enable_decoding=False)

    APP_NAME: str = 'UNABZen API'
    API_V1_PREFIX: str = '/api/v1'
    DEBUG: bool = True
    DATABASE_URL: str = 'sqlite+aiosqlite:///./unabzen.db'
    JWT_SECRET: str = 'dev-secret-change-this-for-production-2026'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOW_DEV_AUTH: bool = True

    AI_ENABLED: bool = False
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = 'gemini-2.5-flash'

    CORS_ORIGINS: List[str] = ['http://localhost:3000', 'http://localhost:8081']
    CRISIS_KEYWORDS: List[str] = [
        'suicidio',
        'autolesion',
        'no quiero vivir',
        'me quiero matar',
        'no aguanto mas',
    ]
    HELP_RESOURCE_NAME: str = 'Bienestar Universitario UNAB'
    HELP_RESOURCE_URL: str = 'https://tu-recurso-institucional.example'

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def split_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

    @field_validator('CRISIS_KEYWORDS', mode='before')
    @classmethod
    def split_keywords(cls, value):
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(',') if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
