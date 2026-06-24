import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # ==================== APP ====================
    APP_NAME: str = "Panel Generator Pro"
    APP_VERSION: str = "2.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    APP_URL: str = os.getenv("APP_URL", "http://localhost:3000")
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    
    # ==================== DATABASE ====================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://panel_user:panel_password@localhost:5432/panel_generator")
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"
    
    # ==================== REDIS ====================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # ==================== SECURITY ====================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ==================== ENCRYPTION ====================
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-32-chars-long!")[:32]
    
    # ==================== CORS ====================
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8000").split(",")
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))
    
    # ==================== STRIPE ====================
    STRIPE_PUBLIC_KEY: Optional[str] = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # ==================== PAYPAL ====================
    PAYPAL_MODE: str = os.getenv("PAYPAL_MODE", "sandbox")
    PAYPAL_CLIENT_ID: Optional[str] = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET: Optional[str] = os.getenv("PAYPAL_CLIENT_SECRET")
    
    # ==================== EMAIL ====================
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@panelgenerator.pro")
    
    # ==================== SMS ====================
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    # ==================== WHATSAPP ====================
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
    WHATSAPP_BUSINESS_PHONE_NUMBER_ID: Optional[str] = os.getenv("WHATSAPP_BUSINESS_PHONE_NUMBER_ID")
    WHATSAPP_BUSINESS_ACCESS_TOKEN: Optional[str] = os.getenv("WHATSAPP_BUSINESS_ACCESS_TOKEN")
    
    # ==================== SHOPIFY ====================
    SHOPIFY_API_KEY: Optional[str] = os.getenv("SHOPIFY_API_KEY")
    SHOPIFY_API_SECRET: Optional[str] = os.getenv("SHOPIFY_API_SECRET")
    SHOPIFY_SHOP_NAME: Optional[str] = os.getenv("SHOPIFY_SHOP_NAME")
    
    # ==================== CRM ====================
    HUBSPOT_API_KEY: Optional[str] = os.getenv("HUBSPOT_API_KEY")
    PIPEDRIVE_API_TOKEN: Optional[str] = os.getenv("PIPEDRIVE_API_TOKEN")
    
    # ==================== ANALYTICS ====================
    GOOGLE_ANALYTICS_ID: Optional[str] = os.getenv("GOOGLE_ANALYTICS_ID")
    MIXPANEL_TOKEN: Optional[str] = os.getenv("MIXPANEL_TOKEN")
    
    # ==================== AWS ====================
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET: Optional[str] = os.getenv("AWS_S3_BUCKET")
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # ==================== FEATURES ====================
    ENABLE_2FA: bool = os.getenv("ENABLE_2FA", "True").lower() == "true"
    ENABLE_OAUTH: bool = os.getenv("ENABLE_OAUTH", "True").lower() == "true"
    ENABLE_MARKETPLACE: bool = os.getenv("ENABLE_MARKETPLACE", "True").lower() == "true"
    ENABLE_WEBHOOKS: bool = os.getenv("ENABLE_WEBHOOKS", "True").lower() == "true"
    ENABLE_API_DOCS: bool = os.getenv("ENABLE_API_DOCS", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
