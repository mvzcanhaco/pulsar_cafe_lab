from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.product import Product


class InventoryRepository(ABC):
    @abstractmethod
    async def list_products(self, available_only: bool = True) -> list[Product]:
        ...

    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Product]:
        ...

    @abstractmethod
    async def create_product(self, product: Product) -> Product:
        ...

    @abstractmethod
    async def update_product(self, product: Product) -> Product:
        ...

    @abstractmethod
    async def delete_product(self, product_id: str) -> bool:
        ...
