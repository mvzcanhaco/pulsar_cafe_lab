from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class OrderState(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"
    PAID = "PAID"
    VOIDED = "VOIDED"
    REFUNDED = "REFUNDED"


# Transições válidas: estado atual → estados permitidos
VALID_TRANSITIONS: dict[OrderState, set[OrderState]] = {
    OrderState.OPEN: {OrderState.LOCKED, OrderState.VOIDED},
    OrderState.LOCKED: {OrderState.PAID, OrderState.OPEN, OrderState.VOIDED},
    OrderState.PAID: {OrderState.REFUNDED},
    OrderState.VOIDED: set(),
    OrderState.REFUNDED: set(),
}


class InvalidStateTransition(Exception):
    """Raised when an order state transition is not allowed."""

    def __init__(self, from_state: OrderState, to_state: OrderState) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Transição inválida: {from_state.value} → {to_state.value}. "
            f"Permitido a partir de {from_state.value}: "
            f"{[s.value for s in VALID_TRANSITIONS.get(from_state, set())] or 'nenhum'}"
        )


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
    line_items: list[LineItem] = Field(default_factory=list)
    note: str = ""
    currency: str = "BRL"
    created_at: datetime = Field(default_factory=datetime.now)
    merchant_id: Optional[str] = None

    @computed_field
    @property
    def total_cents(self) -> int:
        return sum(item.subtotal_cents for item in self.line_items)

    @property
    def total_brl(self) -> float:
        return self.total_cents / 100

    def transition_to(self, new_state: OrderState) -> None:
        """
        Transiciona o pedido para um novo estado.
        Lança InvalidStateTransition se a transição não for permitida.
        """
        allowed = VALID_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            raise InvalidStateTransition(self.state, new_state)
        self.state = new_state
