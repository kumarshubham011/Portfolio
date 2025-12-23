"""
=============================================================================
CONFIGURATION MODULE
=============================================================================
Purpose: Centralized configuration management using Pydantic Settings.

This module:
- Loads environment variables from .env file
- Validates configuration values
- Provides type-safe access to settings
- Sets sensible defaults for development

Usage:
    from app.config import settings
    print(settings.SECRET_KEY)
=============================================================================
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Pydantic Settings automatically:
    - Reads from .env file
    - Converts types (str -> int, etc.)
    - Raises errors for missing required values
    
    All fields with defaults are optional in .env
    Fields without defaults MUST be set.
    """
    
    # -------------------------------------------------------------------------
    # Application Settings
    # -------------------------------------------------------------------------
    DEBUG: bool = True
    SITE_URL: str = "http://localhost:8000"
    
    # -------------------------------------------------------------------------
    # Security Settings
    # -------------------------------------------------------------------------
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"  # JWT signing algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # -------------------------------------------------------------------------
    # Admin Credentials
    # -------------------------------------------------------------------------
    # Used to create initial admin user on first run
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme123"
    
    # -------------------------------------------------------------------------
    # Database Settings
    # -------------------------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./portfolio.db"
    
    # -------------------------------------------------------------------------
    # Site Content Settings
    # -------------------------------------------------------------------------
    SITE_NAME: str = "Your Name"
    SITE_TAGLINE: str = "Software Developer & Lifelong Learner"
    
    # Social Links (all optional)
    GITHUB_URL: Optional[str] = None
    LINKEDIN_URL: Optional[str] = None
    LEETCODE_URL: Optional[str] = None
    EMAIL: Optional[str] = None
    
    # Company Info (optional)
    CURRENT_COMPANY: Optional[str] = None
    COMPANY_URL: Optional[str] = None
    
    # -------------------------------------------------------------------------
    # Pydantic Configuration
    # -------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        # Load from .env file in project root
        env_file=".env",
        # Don't error if .env doesn't exist (use defaults)
        env_file_encoding="utf-8",
        # Case-sensitive environment variables
        case_sensitive=True,
        # Allow extra fields in .env (for flexibility)
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    Using @lru_cache ensures we only read .env once.
    The settings object is then reused across all requests.
    
    Returns:
        Settings: Validated configuration object
    """
    return Settings()


# Convenience export - import this directly
settings = get_settings()
