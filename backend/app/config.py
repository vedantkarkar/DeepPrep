from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "DeepPrep"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql+asyncpg://postgres@localhost:5433/deepprep"
    SYNC_DATABASE_URL: str = "postgresql://postgres@localhost:5433/deepprep"
    AI_PROVIDER: str = "mock"  # mock, cloud, local
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
