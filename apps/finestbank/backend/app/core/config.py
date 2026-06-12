from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FinestBank API"
    app_version: str = "0.1.0"
    debug: bool = False

    # CORS — frontend origins
    allowed_origins: list[str] = ["http://localhost:3000"]

    # Database (Phase 3)
    database_url: str = "postgresql+asyncpg://finestbank:finestbank@localhost:5432/finestbank"

    # Redis (Phase 4)
    redis_url: str = "redis://localhost:6379"

    # Auth (Phase 2)
    clerk_secret_key: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
