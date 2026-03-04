from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://elderos:elderos@localhost:5432/elderos"
    secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    cors_origins: list[str] = ["http://localhost:3000"]
    edge_api_key: str = "edge-device-shared-secret"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
