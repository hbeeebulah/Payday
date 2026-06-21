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

    # --- ALATPay (collection / Transaction Monitoring) --------------------
    alatpay_base_url: str = "https://apibox.alatpay.ng"
    alatpay_api_key: str = ""
    alatpay_public_key: str = ""
    alatpay_business_id: str = ""
    alatpay_webhook_secret: str = ""
    alatpay_timeout_seconds: float = 30.0
    alatpay_wallet_type: int = 2
    wema_bank_code: str = "035"
    alatpay_disbursement_concurrency: int = 10

    # Which backend actually moves money for a payroll run:
    #   "collection" -> the ALATPay collection rails (default; demo/sandbox)
    #   "payout"     -> the real Wema Merchant Payout (NIP disbursement) API
    disbursement_mode: str = "collection"

    # --- Wema Merchant Payout (real NIP disbursement) ---------------------
    # Production base: https://apps.wemabank.com/WemaAPIService/
    payout_base_url: str = "https://apps.wemabank.com/WemaAPIService/"
    payout_username: str = ""
    payout_password: str = ""
    # Vendor identifier supplied by the bank; sent as the `VendorId` header.
    payout_vendor_id: str = ""
    # Azure APIM subscription key (Ocp-Apim-Subscription-Key); optional.
    payout_subscription_key: str = ""
    # AES-128 key + IV (16 ASCII chars each) supplied by the bank. The values
    # below are the public SANDBOX key/IV and MUST be overridden in production.
    payout_encryption_key: str = ")KCSWITHC%^$$%@H"
    payout_encryption_iv: str = "#$%#^%KCSWITC945"
    # Merchant debit/source account profiled with Wema.
    payout_source_account: str = ""
    # Display name shown to beneficiaries as the originator.
    payout_originator_name: str = "Payday"
    payout_timeout_seconds: float = 30.0

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

    @property
    def payout_enabled(self) -> bool:
        return self.disbursement_mode.lower() == "payout"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
