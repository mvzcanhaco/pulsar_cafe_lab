from dataclasses import dataclass


@dataclass(frozen=True)
class SitefSaleConfig:
    """
    Configuration for a Sitef sale transaction.
    Mirrors SitefSaleConfig.kt from the Android app.
    """
    sitef_ip: str
    sitef_port: int
    company_id: str          # CNPJ da empresa
    terminal_id: str         # ID do terminal (PDV)
    isv_app_id: str          # ID do aplicativo ISV Fiserv
    api_version: str = "0"
    timeout_seconds: int = 60
