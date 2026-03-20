from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    async def save_payment(self, payment: Payment) -> Payment:
        ...

    @abstractmethod
    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        ...

    @abstractmethod
    async def list_payments_for_order(self, order_id: str) -> list[Payment]:
        ...

    @abstractmethod
    async def get_by_idempotency_key(self, key: str) -> Optional[Payment]:
        """Retorna pagamento existente com essa chave, se houver."""
        ...
