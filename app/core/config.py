from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    GITHUB_TOKEN: str
    GITHUB_WEBHOOK_SECRET: str = ""  # Opcional en desarrollo

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
