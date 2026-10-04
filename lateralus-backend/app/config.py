import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_timeout: float = 3.0
    openai_max_retries: int = 0
    redis_url: str = "redis://localhost:6379"
    redis_checkpoint_enabled: bool = True
    postgres_dsn: str = "postgresql://root:root@localhost:5432/lateralus_db"
    postgres_pool_enabled: bool = True


def get_settings() -> Settings:
    try:
        openai_api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:
        raise KeyError(
            "OPENAI_API_KEY not found in environment variables. Please set it in your .env file."
        )

    return Settings(
        openai_api_key=openai_api_key,
        openai_model=os.getenv("OPENAI_MODEL", Settings.openai_model),
        openai_timeout=float(os.getenv("OPENAI_TIMEOUT", Settings.openai_timeout)),
        openai_max_retries=int(os.getenv("OPENAI_MAX_RETRIES", Settings.openai_max_retries)),
        redis_url=os.getenv("REDIS_URL", Settings.redis_url),
        redis_checkpoint_enabled=_env_bool("REDIS_CHECKPOINT_ENABLED"),
        postgres_dsn=os.getenv("POSTGRES_URL", Settings.postgres_dsn),
        postgres_pool_enabled=_env_bool("POSTGRES_POOL_ENABLED"),
    )
