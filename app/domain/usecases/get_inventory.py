from app.domain.models.product import Product
from app.domain.repositories.inventory_repository import InventoryRepository


class GetInventoryUseCase:
    def __init__(self, repository: InventoryRepository) -> None:
        self._repo = repository

    async def execute(self, available_only: bool = True) -> list[Product]:
        return await self._repo.list_products(available_only=available_only)
