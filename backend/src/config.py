from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    AMAZON_API_KEY: str
    AMAZON_SECRET_KEY: str
    AMAZON_PARTNER_TAG: str
    
    # MongoDB
    MONGODB_URI: str
    MONGODB_DB: str
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    
    # Qdrant
    QDRANT_URL: str
    QDRANT_COLLECTION: str
    QDRANT_API_KEY: str
    QDRANT_HOST: str
    QDRANT_CLUSTER: str
    
    # App Settings
    APP_NAME: str
    APP_VERSION: str
    ENVIRONMENT: str
    LOG_LEVEL: str
    
    # JWT Settings
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
