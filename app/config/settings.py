from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "prod"
    FRONTEND_URL: str = "https://ginarr.ai"
    DEBUG: bool = False

    DB_USER: str = "username"
    DB_PASSWORD: str = "userpassword"
    DB_HOST: str = "db-budgeter"
    DB_NAME: str = "dbname"
    DB_PORT: int = 5432

    # CELERY_BROKER_URL: str = "redis://redis-budgeter:6379"
    # CELERY_RESULT_BACKEND: str = "redis://redis-budgeter:6379"

    # TEST_LOG_FILE: str = "test.log"

    # DAILY_DB_BACKUP_HOUR: str = "14"
    # DAILY_DB_BACKUP_MINUTE: str = "00"
    # DB_BACKUP_DIR: str = "backup"

    # ADMINS_NOTIFICATION_EMAILS: list[str] = []

    # MAIL_USERNAME: str = "example@example.com"
    # MAIL_PASSWORD: str = "*************"
    # MAIL_FROM: str = "example@example.com"
    # MAIL_PORT: int = 587
    # MAIL_SERVER: str = "smtp.gmail.com"
    # MAIL_FROM_NAME: str = "OrgFin.run Team"
    # MAIL_STARTTLS: bool = True
    # MAIL_SSL_TLS: bool = False
    # USE_CREDENTIALS: bool = True

    # JWT expiration time in minutes
    LOGIN_SESSION_EXPIRATION_MINUTES: int = 30

    # GOOGLE_CLIENT_ID: str = "123"

    SECRET_KEY: str = "111111111"

    EMBEDDING_PROVIDER: str = "openai"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_EMBEDDING_MAX_CHUNK_SIZE: int = 8191
    OPENAI_API_KEY: SecretStr = SecretStr("sk-proj-123")

    model_config = SettingsConfigDict(env_file=(".env", ".env.local", ".env.prod"))


settings = Settings()
