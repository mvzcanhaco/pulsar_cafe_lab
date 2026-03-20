from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, computed_field


class OrderState(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"
    PAID = "PAID"
    VOIDED = "VOIDED"
    REFUNDED = "REFUNDED"


class LineItem(BaseModel):
    id: str
    name: str
    price_cents: int
    quantity: int = 1

    @property
    def subtotal_cents(self) -> int:
        return self.price_cents * self.quantity


class Order(BaseModel):
    id: str
    state: OrderState = OrderState.OPEN
    line_items: list[LineItem] = []
    note: str = ""
    currency: str = "BRL"
    created_at: datetime = datetime.now()
    merchant_id: Optional[str] = None

    @computed_field
    @property
    def total_cents(self) -> int:
        return sum(item.subtotal_cents for item in self.line_items)

    @property
    def total_brl(self) -> float:
        return self.total_cents / 100
