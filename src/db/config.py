from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    mongo_uri: str

    class Config:
        env_file = ".env"


settings = Settings()