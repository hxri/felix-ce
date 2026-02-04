from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    fal_key: str

    class Config:
        env_file = ".env"


settings = Settings()
