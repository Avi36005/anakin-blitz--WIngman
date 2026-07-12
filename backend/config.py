from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # All optional so the app boots with NO keys (mock mode).
    anakin_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    redis_url: str = "redis://localhost:6379"
    pinecone_api_key: Optional[str] = None
    pinecone_index: str = "wingman-precedents"
    pinecone_environment: str = "us-east-1"
    port: int = 8000

    # Anakin endpoints
    wire_task_url: str = "https://api.anakin.io/v1/wire/task"
    wire_job_url: str = "https://api.anakin.io/v1/wire/jobs"
    scraper_url: str = "https://api.anakin.io/v1/url-scraper"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def has_anakin(self) -> bool:
        return bool(self.anakin_api_key)

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()