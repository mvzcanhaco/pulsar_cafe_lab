from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.order import Order, OrderState


class OrderRepository(ABC):
    @abstractmethod
    async def list_orders(self, state: Optional[OrderState] = None) -> list[Order]:
        ...

    @abstractmethod
    async def get_order(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        ...

    @abstractmethod
    async def update_order(self, order: Order) -> Order:
        ...
