from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    mongo_uri: str = Field(..., env='SCALINGO_MONGO_URL')

    # class Config:
    #     env_file = ".env"


settings = Settings()