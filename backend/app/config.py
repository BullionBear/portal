from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PORTAL_")

    company_name: str = "Lynkora"
    tagline: str = "Company applications at a glance"
    apps_file: Path = Path(__file__).resolve().parent / "data" / "apps.json"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
