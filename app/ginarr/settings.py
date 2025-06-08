from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr = SecretStr("sk-proj-123")
    DEEPSEEK_API_KEY: SecretStr = SecretStr("sk-proj-123")
    GOOGLE_API_KEY: SecretStr = SecretStr("sk-proj-123")

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    LLM_MODEL: str = "mistral"
    LLM_TEMPERATURE: float = 0.0
    LLM_USE_LOCAL: bool = True

    MEMORY_SQLITE_PATH: Path = Path(__file__).parent / "memory.sqlite"

    model_config = SettingsConfigDict(env_file=Path(__file__).parent / ".env.ginarr", env_file_encoding="utf-8")


settings = Settings()
