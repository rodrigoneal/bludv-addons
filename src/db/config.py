from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    mongo_uri: str = Field(..., env="MONGO_URI")

    # class Config:
    #     env_file = ".env"


settings = Settings()