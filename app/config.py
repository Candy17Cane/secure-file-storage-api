from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


class Settings(BaseSettings):
    # ===== APP =====
    APP_NAME: str = 'Secure File Storage API'
    DEBUG: bool = False

    # ===== DATABASE =====
    DATABASE_URL: str

    # ===== SECURITY =====
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ===== FILE STORAGE =====
    STORAGE_PATH: str = 'storage/encrypted'

    # ===== CRYPTO =====
    MASTER_KEY: str

    class Config:
        env_file = BASE_DIR / '.env'
        env_file_encrypted = 'utf-8'

# создаем единый объект настроек
settings = Settings()