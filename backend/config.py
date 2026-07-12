from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # All optional so the app boots with NO keys (mock mode).
    anakin_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    groq_api_keys: Optional[str] = None  # comma/space/newline separated pool
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
    def groq_keys(self) -> list[str]:
        """Full pool of Groq keys (from GROQ_API_KEYS + GROQ_API_KEY), de-duped."""
        import re
        raw = " ".join(filter(None, [self.groq_api_keys, self.groq_api_key]))
        keys = [k for k in re.split(r"[\s,]+", raw) if k.startswith("gsk_")]
        seen, out = set(), []
        for k in keys:
            if k not in seen:
                seen.add(k)
                out.append(k)
        return out

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_keys)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()