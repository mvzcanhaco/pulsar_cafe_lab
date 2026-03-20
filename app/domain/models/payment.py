from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PaymentResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    CANCEL = "CANCEL"
    AUTH = "AUTH"
    PARTIAL = "PARTIAL"
    REFUNDED = "REFUNDED"


class CardType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    VOUCHER = "VOUCHER"
    PIX = "PIX"
    UNKNOWN = "UNKNOWN"


class Payment(BaseModel):
    id: str
    order_id: str
    amount_cents: int
    tip_amount_cents: int = 0
    tax_amount_cents: int = 0
    result: PaymentResult
    card_type: CardType = CardType.UNKNOWN
    last4: str = ""
    # Sitef-specific fields
    nsu: str = ""
    auth_code: str = ""
    card_brand: str = ""
    installments: int = 1
    merchant_receipt: str = ""
    customer_receipt: str = ""
    created_at: datetime = datetime.now()
    error_message: Optional[str] = None

    @property
    def amount_brl(self) -> float:
        return self.amount_cents / 100
