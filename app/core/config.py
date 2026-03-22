from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGO_URL: str = Field(default="mongodb://localhost:27017")
    MONGO_DB: str = Field(default="task_tracker")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    RABBITMQ_URL: str = Field(default="amqp://guest:guest@rabbitmq:5672//")
    OPENAI_API_KEY: str = Field(default="your_key")
    
    SECRET_KEY: str = Field(default="super-secret-key-change-it-in-prod")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
