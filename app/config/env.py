"""Konfigurasi aplikasi menggunakan Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Kelas konfigurasi aplikasi yang memuat semua environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Email SMTP (Zoho Mail)
    SMTP_HOST: Optional[str] = "smtp.zoho.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    
    # App
    APP_NAME: str = "Auth Service"
    RESET_TOKEN_EXPIRE_MINUTES: int = 15
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS
    CORS_ORIGINS: str = "*"  # Comma-separated list atau "*" untuk semua
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    class Config:
        env_file = str(BASE_DIR / ".env")
        case_sensitive = True


settings = Settings()
