from typing import Optional, Union
from pathlib import Path
from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )

    # Project Info
    PROJECT_NAME: str = "RAG Backend"
    API_V1_STR: str = "/api/v1"
    
    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # LLM (Required)
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: str # Required for Groq
    
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    # Default to Groq model
    EMBEDDING_MODEL: str = "nomic-embed-text-v1.5"



    # Vector DB
    # Allows HTTP URL or local path string
    VECTOR_DB_URL: Union[str, AnyHttpUrl] = "http://localhost:6333" 
    VECTOR_DB_API_KEY: Optional[str] = None

    VECTOR_COLLECTION_NAME: str = "documents"

    @computed_field
    @property
    def vector_db_host(self) -> str:
        return str(self.VECTOR_DB_URL)

    def create_dirs(self):
        """Ensure critical directories exist"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.create_dirs()
