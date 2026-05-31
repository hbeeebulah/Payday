"""Application configuration loaded from the environment.

Settings are validated once at import time and cached via :func:`get_settings`
so they can be cheaply injected into routes, services and the database layer.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application -------------------------------------------------------
    app_env: str = "development"
    debug: bool = True
    project_name: str = "Payday API"
    api_prefix: str = "/api/v1"

    # --- CORS --------------------------------------------------------------
    backend_cors_origins: list[str] = ["http://localhost:3000"]

    # --- Database ----------------------------------------------------------
    # Default to a local async SQLite file so the service boots with zero
    # external dependencies; production overrides this with a Postgres URL.
    database_url: str = "sqlite+aiosqlite:///./payday.db"

    # --- ALATPay -----------------------------------------------------------
    # Base URL of the ALATPay (Wema Bank) API gateway.
    alatpay_base_url: str = "https://apibox.alatpay.ng"
    # Subscription/secret key injected into the `Ocp-Apim-Subscription-Key`
    # header on every outbound request (this is what authenticates the call).
    alatpay_api_key: str = ""
    # Merchant public key (used by the checkout SDK and kept for completeness).
    alatpay_public_key: str = ""
    # Merchant business identifier; ALATPay expects this in request bodies and
    # query strings rather than as a header.
    alatpay_business_id: str = ""
    # Secret used to verify the signature on inbound ALATPay webhooks.
    alatpay_webhook_secret: str = ""
    # Outbound HTTP timeout (seconds).
    alatpay_timeout_seconds: float = 30.0
    # Static wallet type used for the per-business Payroll Wallet:
    #   1 = Individual (BVN + OTP verified), 2 = Collection wallet.
    alatpay_wallet_type: int = 2
    # Bank code that identifies Wema Bank accounts; these are paid via the
    # direct-debit "Pay with Bank Details" flow instead of bank transfer.
    wema_bank_code: str = "035"
    # Bounded concurrency for parallel disbursement requests.
    alatpay_disbursement_concurrency: int = 10

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        """Allow CORS origins to be provided as a comma separated string."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
