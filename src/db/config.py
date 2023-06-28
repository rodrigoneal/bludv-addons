from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    MONGO_URI: str = Field(..., env="MONGO_URI")

    # class Config:
    #     env_file = ".env"


settings = Settings()
