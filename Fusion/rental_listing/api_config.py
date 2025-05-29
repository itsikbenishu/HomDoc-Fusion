from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    RENTCAST_RENTAL_LISTING_API: str
    RENTCAST_RENTAL_LISTING_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env", 
        env_file_encoding='utf-8',
        extra='ignore'
    )

api_settings = Settings()
