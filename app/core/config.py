from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = ""
    SESSION_SECRET: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    DEBUG: bool = False

    @model_validator(mode="after")
    def set_secret_key(self):
        if not self.SECRET_KEY and self.SESSION_SECRET:
            self.SECRET_KEY = self.SESSION_SECRET
        if not self.SECRET_KEY:
            raise ValueError(
                "Необходимо задать SECRET_KEY или SESSION_SECRET в переменных окружения"
            )
        return self

    class Config:
        env_file = ".env"


settings = Settings()
