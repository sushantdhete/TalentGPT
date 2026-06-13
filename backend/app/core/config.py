"""
TalentGPT - Core Configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TalentGPT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/talentgpt"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI / LLM
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""  # fallback
    
    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # FAISS
    FAISS_INDEX_PATH: str = "data/faiss_index"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://talentgpt.ai",
    ]
    
    # Scoring Weights
    WEIGHT_SKILLS: float = 0.35
    WEIGHT_EXPERIENCE: float = 0.25
    WEIGHT_LEARNING: float = 0.15
    WEIGHT_LEADERSHIP: float = 0.10
    WEIGHT_BEHAVIOR: float = 0.10
    WEIGHT_CULTURE: float = 0.05
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
