import os
from typing import Any, Dict, Optional
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "CircuitGPT"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days

    # Ports
    FRONTEND_PORT: int = 3000
    BACKEND_PORT: int = 8000
    NGINX_PORT: int = 80

    # PostgreSQL Database Settings
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "circuitgpt"
    POSTGRES_PASSWORD: str = "circuitsecurepass"
    POSTGRES_DB: str = "circuitgpt_db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str) and v:
            return v
            
        data = info.data
        user = data.get("POSTGRES_USER")
        password = data.get("POSTGRES_PASSWORD")
        server = data.get("POSTGRES_SERVER")
        port = data.get("POSTGRES_PORT")
        db = data.get("POSTGRES_DB")
        
        return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

    # Redis Settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redissecurepass"

    @property
    def REDIS_URI(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # Qdrant Vector DB Settings
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    # MinIO Object Storage Settings
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadminsecure"
    MINIO_PORT: int = 9000
    MINIO_CONSOLE_PORT: int = 9001
    MINIO_BUCKET_NAME: str = "circuitgpt-bucket"
    MINIO_ENDPOINT: str = "http://minio:9000"
    MINIO_PUBLIC_ENDPOINT: str = "http://localhost:9000"

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_DOCUMENT_EXTENSIONS: str = ".pdf,.doc,.docx"
    ALLOWED_VIDEO_EXTENSIONS: str = ".mp4,.webm,.mkv,.mov"
    ALLOWED_BOOK_EXTENSIONS: str = ".pdf"
    ALLOWED_PYQ_EXTENSIONS: str = ".pdf"

    # LLM Settings & Provider Abstraction
    LLM_PROVIDER: str = "nvidia"
    NVIDIA_API_KEY: Optional[str] = None
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b"
    NVIDIA_REASONING_EFFORT: str = "high"  # none | medium | high
    NVIDIA_MAX_TOKENS: int = 16384
    NVIDIA_TEMPERATURE: float = 1.0
    NVIDIA_TOP_P: float = 0.95

    # Context Window & RAG Limits
    AI_CONTEXT_WINDOW_TOKENS: int = 32000
    AI_RAG_TOP_K: int = 8
    AI_MEMORY_TOP_K: int = 5
    AI_MAX_RECENT_MESSAGES: int = 20

    # Legacy External APIs (kept for backwards compatibility)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    TAVILY_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None

    # NextJS
    NEXT_PUBLIC_API_URL: str = "http://localhost/api/v1"

    # Load environment file dynamically by searching upwards for .env
    @classmethod
    def _find_env_file(cls) -> str:
        current = os.path.abspath(__file__)
        for _ in range(6):
            current = os.path.dirname(current)
            env_path = os.path.join(current, ".env")
            if os.path.exists(env_path):
                return env_path
        return ".env"

    model_config = SettingsConfigDict(
        env_file=_find_env_file.__func__(None),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
