"""
Конфигурация для Check Your Crypto
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


def get_database_url() -> str:
    """Получить URL базы данных для SQLAlchemy"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is required!")

    # Конвертируем postgres:// в postgresql:// для SQLAlchemy
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return db_url


class Settings(BaseSettings):
    """Настройки приложения"""

    # Bot
    bot_token: str = Field(description="Telegram bot token", alias="BOT_TOKEN")
    alert_bot_token: Optional[str] = Field(default=None, description="Alert bot token", alias="ALERT_BOT_TOKEN")
    ops_chat_id: Optional[str] = Field(default=None, description="Operations chat ID", alias="OPS_CHAT_ID")

    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/checkyourcrypto",
        description="Database URL",
        alias="DATABASE_URL",
    )
    sqlalchemy_database_url: Optional[str] = Field(
        default=None, description="SQLAlchemy database URL", alias="SQLALCHEMY_DATABASE_URL"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Конвертируем postgres:// в postgresql:// для SQLAlchemy
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)

    # MetaSleuth API
    metasleuth_api_key: Optional[str] = Field(default=None, description="MetaSleuth API key", alias="METASLEUTH_API_KEY")
    metasleuth_api_url: str = Field(default="https://api.metasleuth.io", description="MetaSleuth API URL")
    metasleuth_wallet_screening_key: Optional[str] = Field(
        default=None, description="MetaSleuth wallet screening key", alias="METASLEUTH_WALLET_SCREENING_KEY"
    )
    metasleuth_address_label_key: Optional[str] = Field(
        default=None, description="MetaSleuth address label key", alias="METASLEUTH_ADDRESS_LABEL_KEY"
    )
    mock_metasleuth: bool = Field(default=False, description="Mock MetaSleuth", alias="MOCK_METASLEUTH")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key", alias="OPENAI_API_KEY")

    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN", alias="SENTRY_DSN")

    # Payment
    binance_pay_api_key: Optional[str] = Field(default=None, description="Binance Pay API key", alias="BINANCE_PAY_API_KEY")
    binance_pay_secret: Optional[str] = Field(default=None, description="Binance Pay secret", alias="BINANCE_PAY_SECRET")

    # Admin
    admin_secret: Optional[str] = Field(default=None, description="Admin secret", alias="ADMIN_SECRET")
    django_secret_key: Optional[str] = Field(default=None, description="Django secret key", alias="DJANGO_SECRET_KEY")

    # Limits
    free_limit_minutes: int = Field(default=10, description="Free check limit in minutes", alias="FREE_LIMIT_MINUTES")

    # AWS
    aws_s3_bucket: Optional[str] = Field(default=None, description="AWS S3 bucket", alias="AWS_S3_BUCKET")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(
        default=None, description="AWS secret access key", alias="AWS_SECRET_ACCESS_KEY"
    )
    aws_region: Optional[str] = Field(default=None, description="AWS region", alias="AWS_REGION")

    # Slack
    optional_slack_webhook_url: Optional[str] = Field(
        default=None, description="Slack webhook URL", alias="OPTIONAL_SLACK_WEBHOOK_URL"
    )

    # Admin API
    admin_api_url: str = Field(description="Admin API URL", alias="ADMIN_API_URL")

    # Heroku
    heroku_app_name: str = Field(
        default="checkyourcrypto-bot-87c446f24699", description="Heroku app name", alias="HEROKU_APP_NAME"
    )

    # Environment
    environment: str = Field(default="development", description="Environment", alias="ENVIRONMENT")
    debug: bool = Field(default=False, description="Debug mode", alias="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Создаем глобальный экземпляр настроек
settings = Settings()
