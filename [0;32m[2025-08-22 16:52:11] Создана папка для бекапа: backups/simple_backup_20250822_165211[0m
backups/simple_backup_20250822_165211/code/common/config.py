"""
Конфигурация приложения Check Your Crypto
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    bot_token: str = Field(description="Telegram bot token", alias="BOT_TOKEN")
    alert_bot_token: str = Field(description="Alert bot token", alias="ALERT_BOT_TOKEN")
    ops_chat_id: str = Field(description="Operations chat ID", alias="OPS_CHAT_ID")
    
    # MetaSleuth
    metasleuth_wallet_screening_key: str = Field(description="MetaSleuth wallet screening API key", alias="METASLEUTH_WALLET_SCREENING_KEY")
    metasleuth_address_label_key: str = Field(description="MetaSleuth address label API key", alias="METASLEUTH_ADDRESS_LABEL_KEY")
    mock_metasleuth: bool = Field(default=False, description="Mock MetaSleuth responses", alias="MOCK_METASLEUTH")
    
    # Database
    database_url: str = Field(default="", description="Database URL", alias="SQLALCHEMY_DATABASE_URL")
    
    @property
    def sqlalchemy_database_url(self) -> str:
        """Получить URL базы данных для SQLAlchemy"""
        # Если SQLALCHEMY_DATABASE_URL задан явно, используем его
        if self.database_url:
            return self.database_url
        
        # Иначе используем DATABASE_URL и конвертируем для SQLAlchemy
        django_db_url = os.getenv('DATABASE_URL', 'sqlite:///./checkyourcrypto.db')
        
        if django_db_url.startswith('postgres://'):
            django_db_url = django_db_url.replace('postgres://', 'postgresql://', 1)
        
        if django_db_url.startswith('postgresql://'):
            # Конвертируем для asyncpg
            return django_db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        elif django_db_url.startswith('sqlite://'):
            # Конвертируем для aiosqlite
            return django_db_url.replace('sqlite://', 'sqlite+aiosqlite://', 1)
        else:
            return django_db_url
    
    # Django
    admin_secret: str = Field(description="Admin secret key", alias="ADMIN_SECRET")
    django_secret_key: str = Field(description="Django secret key", alias="DJANGO_SECRET_KEY")
    
    # Settings
    free_limit_minutes: int = Field(default=10, description="Free check limit in minutes", alias="FREE_LIMIT_MINUTES")
    
    # Check Limits System
    new_user_days: int = Field(default=3, description="New user grace period in days", alias="NEW_USER_DAYS")
    max_checks_per_day: int = Field(default=50, description="Maximum checks per day", alias="MAX_CHECKS_PER_DAY")
    min_interval_seconds: int = Field(default=3, description="Minimum interval between checks", alias="MIN_INTERVAL_SECONDS")
    
    # AWS S3
    aws_s3_bucket: str = Field(description="AWS S3 bucket name", alias="AWS_S3_BUCKET")
    aws_access_key_id: str = Field(description="AWS access key ID", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(description="AWS secret access key", alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", description="AWS region", alias="AWS_REGION")
    
    # Optional
    slack_webhook_url: Optional[str] = Field(default=None, description="Slack webhook URL", alias="OPTIONAL_SLACK_WEBHOOK_URL")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN", alias="SENTRY_DSN")
    
    # Environment
    environment: str = Field(default="development", description="Environment name", alias="ENVIRONMENT")
    debug: bool = Field(default=True, description="Debug mode", alias="DEBUG")
    
    # Supported chains
    supported_chains: List[str] = [
        'btc', 'eth', 'tron', 'solana', 'optimism', 'cronos', 'bsc', 
        'gnosis', 'polygon', 'manta', 'bittorrent', 'fantom', 'boba', 
        'zksync', 'clv', 'polygonzkevm', 'wemix', 'moonbeam', 'moonriver', 
        'mantle', 'base', 'arbitrum', 'celo', 'avalanche', 'linea', 
        'blast', 'aurora'
    ]
    
    # OpenAI GPT
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        env_prefix="",
        env_nested_delimiter="__",
    )


# Глобальный экземпляр настроек
settings = Settings()


def get_settings() -> Settings:
    """Получить настройки приложения"""
    return settings
