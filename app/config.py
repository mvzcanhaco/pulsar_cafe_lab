from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_name: str = "Pulsar Café Lab"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "sqlite+aiosqlite:///./pulsar_cafe.db"

    # Fiserv / Sitef
    fiserv_sitef_ip: str = "127.0.0.1"
    fiserv_sitef_port: int = 4096
    fiserv_company_id: str = ""
    fiserv_terminal_id: str = ""
    fiserv_merchant_cnpj: str = ""
    fiserv_isv_app_id: str = ""
    fiserv_api_version: str = "0"
    fiserv_timeout_seconds: int = 60

    # Merchant defaults
    merchant_currency: str = "BRL"


settings = Settings()
