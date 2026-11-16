import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "FORGE 2.0"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    FORGE_ROOT: Path = BASE_DIR.parent
    PARENT_DIR: Path = FORGE_ROOT.parent
    
    # Study Cursor project path
    STUDY_CURSOR_DIR: Path = PARENT_DIR / "study-cursor"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/forge.db"
    
    # Security
    API_SECRET_KEY: str = "forge-secret-key-development-local-only-replace-in-prod"
    LAN_ACCESS_ENABLED: bool = False
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "http://localhost:5173", # Study cursor vite dev
        "*"
    ]
    
    # Focus Session Defaults (minutes)
    POMODORO_DURATION_MINUTES: int = 50
    SHORT_BREAK_MINUTES: int = 10
    LONG_BREAK_MINUTES: int = 30
    APTITUDE_DAILY_MINUTES: int = 15 # Mandatory 15-minute aptitude rule

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
