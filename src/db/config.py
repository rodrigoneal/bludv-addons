from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    mongo_uri: str = Field(..., env='mongo_uri')

    # class Config:
    #     env_file = ".env"


settings = Settings()