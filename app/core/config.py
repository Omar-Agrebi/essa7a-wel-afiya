"""Configuration settings for the application."""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        DATABASE_URL (str): The PostgreSQL database connection URI string.
        SECRET_KEY (str): Secret key for JWT signing and cryptographic operations.
        CORS_ORIGINS (str): Comma-separated list of allowed CORS origins.
        ENVIRONMENT (str): The environment the app is running in.
        SCRAPER_MODE (str): Controls scraper behavior (live | mock). Defaults to "mock".
        RECOMMENDATION_W1 (float): Weight for similarity score. Defaults to 0.5.
        RECOMMENDATION_W2 (float): Weight for level match score. Defaults to 0.3.
        RECOMMENDATION_W3 (float): Weight for recency score. Defaults to 0.2.
    """
    DATABASE_URL: str
    SECRET_KEY: str
    CORS_ORIGINS: str
    ENVIRONMENT: str
    SCRAPER_MODE: str = "mock"
    RECOMMENDATION_W1: float = 0.5
    RECOMMENDATION_W2: float = 0.3
    RECOMMENDATION_W3: float = 0.2
    
    # JWT and Authentication Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
