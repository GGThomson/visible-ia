"""Settings loaded from environment variables and the local .env file.

Secrets are typed as SecretStr so they never show up in reprs or logs.
"""

from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Env = Literal["dev", "prod"]

# Variable name -> task that first needs it (shown by `config check`).
REQUIRED_PER_ENV = ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY")
LATER = {
    "SUPABASE_DB_URL_{env}": "C1-T03 (migraciones)",
    "CLOUDFLARE_ACCOUNT_ID": "C1-T06 (despliegue de la landing)",
    "CLOUDFLARE_API_TOKEN": "C1-T06 (despliegue de la landing)",
    "OPENAI_API_KEY": "C3 (motor)",
    "SERPAPI_API_KEY": "C3 (motor)",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    visible_ia_env: Env = "dev"

    supabase_url_dev: str | None = None
    supabase_anon_key_dev: SecretStr | None = None
    supabase_service_role_key_dev: SecretStr | None = None
    supabase_db_url_dev: SecretStr | None = None

    supabase_url_prod: str | None = None
    supabase_anon_key_prod: SecretStr | None = None
    supabase_service_role_key_prod: SecretStr | None = None
    supabase_db_url_prod: SecretStr | None = None

    cloudflare_account_id: str | None = None
    cloudflare_api_token: SecretStr | None = None

    openai_api_key: SecretStr | None = None
    serpapi_api_key: SecretStr | None = None

    # OpenAI cap approved by the Director on 2026-09-26 (US$5 prepaid, auto-recharge off).
    monthly_budget_usd: float = 5.0
    serpapi_monthly_quota: int = 250

    @field_validator("supabase_url_dev", "supabase_url_prod", mode="before")
    @classmethod
    def _normalize_url(cls, value: object) -> object:
        # Values pasted into GitHub Secrets often lack the scheme or carry quotes/spaces.
        if not isinstance(value, str):
            return value
        cleaned = value.strip().strip("\"'").strip().rstrip("/")
        if not cleaned:
            return None
        if not cleaned.startswith(("https://", "http://")):
            cleaned = f"https://{cleaned}"
        return cleaned

    def value(self, name: str) -> object:
        """Return the raw field for an env var name (e.g. 'SUPABASE_URL_DEV')."""
        return getattr(self, name.lower())

    def missing_required(self, env: Env | None = None) -> list[str]:
        """Variables the CLI cannot work without, for the given (or active) environment."""
        env = env or self.visible_ia_env
        names = [f"{base}_{env.upper()}" for base in REQUIRED_PER_ENV]
        return [n for n in names if not _is_set(self.value(n))]

    def missing_later(self, env: Env | None = None) -> dict[str, str]:
        """Variables not needed yet, mapped to the task that will need them."""
        env = env or self.visible_ia_env
        out = {}
        for pattern, task in LATER.items():
            name = pattern.format(env=env.upper())
            if not _is_set(self.value(name)):
                out[name] = task
        return out


def _is_set(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, SecretStr):
        return bool(value.get_secret_value().strip())
    return bool(str(value).strip())


def get_settings() -> Settings:
    return Settings()
