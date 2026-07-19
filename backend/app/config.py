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

    # Discord OAuth (admin / private API)
    discord_client_id: str = ""
    discord_client_secret: str = ""
    discord_guild_id: str = ""
    discord_redirect_uri: str = (
        "https://portal.lynkora.com/api/public/auth/discord/callback"
    )
    session_secret: str = "dev-only-change-me"
    cookie_secure: bool = True
    # Optional: host-only cookie when empty
    cookie_domain: str = ""


settings = Settings()
