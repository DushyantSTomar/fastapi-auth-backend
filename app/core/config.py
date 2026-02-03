from pydantic_settings import BaseSettings, SettingsConfigDict
import sys

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SQLALCHEMY_DATABASE_URI: str
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

try:
    settings = Settings()
    print("INFO:  Environment variables loaded successfully.")
except Exception as e:
    print(f"ERROR: Failed to load environment variables: {e}")
    sys.exit(1)
