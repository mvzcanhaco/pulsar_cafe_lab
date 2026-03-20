from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SitefSaleRequest:
    """
    Payload for a Sitef sale request.
    Mirrors SitefSaleRequest.kt + SitefSaleRequestBuilder.kt from the Android app.
    """
    order_id: str
    amount_cents: int                           # valor em centavos
    installments: int = 1
    invoice_number: str = field(default="")     # NSU local gerado no momento
    timestamp: str = field(default="")          # yyyyMMddHHmmss

    def __post_init__(self) -> None:
        if not self.invoice_number:
            self.invoice_number = self.order_id[:12].replace("-", "")
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    def to_api_dict(self) -> dict:
        return {
            "valorVenda": str(self.amount_cents),
            "numeroPedido": self.invoice_number,
            "dataHoraTransacao": self.timestamp,
            "numeroParcelas": str(self.installments),
        }
