from pathlib import Path

from icecream import ic
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr = SecretStr("sk-proj-123")

    MEMORY_SQLITE_PATH: Path = Path(__file__).parent / "memory.sqlite"

    model_config = SettingsConfigDict(env_file=Path(__file__).parent / ".env.ginarr", env_file_encoding="utf-8")


settings = Settings()
