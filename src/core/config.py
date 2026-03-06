from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from typing import Optional
from pydantic import model_validator

class Settings(BaseSettings):
    # Optional individual components for local development
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None

    # Allows Render.com to pass the full URL directly
    DATABASE_URL: Optional[str] = None

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 7*24*60
    
    @model_validator(mode='after')
    def assemble_db_connection(self) -> 'Settings':
        if not self.DATABASE_URL:
            self.DATABASE_URL = str(MultiHostUrl.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=int(self.POSTGRES_PORT) if self.POSTGRES_PORT else 5432,
                path=self.POSTGRES_DB,
            ))
        return self
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

settings = Settings()
