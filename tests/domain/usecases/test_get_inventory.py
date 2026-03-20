import pytest

from app.domain.models.product import PriceType, Product
from app.domain.usecases.get_inventory import GetInventoryUseCase


class MockInventoryRepo:
    def __init__(self, products: list[Product]) -> None:
        self._products = products

    async def list_products(self, available_only: bool = True) -> list[Product]:
        if available_only:
            return [p for p in self._products if p.available]
        return self._products

    async def get_product(self, product_id: str):
        return next((p for p in self._products if p.id == product_id), None)

    async def create_product(self, product): return product
    async def update_product(self, product): return product
    async def delete_product(self, product_id): return True


@pytest.fixture
def sample_products():
    return [
        Product(id="1", name="Café Expresso", price_cents=500, category="Café", available=True),
        Product(id="2", name="Croissant", price_cents=800, category="Padaria", available=True),
        Product(id="3", name="Produto Inativo", price_cents=100, available=False),
    ]


@pytest.mark.asyncio
async def test_get_inventory_returns_available_only(sample_products):
    repo = MockInventoryRepo(sample_products)
    usecase = GetInventoryUseCase(repo)

    result = await usecase.execute(available_only=True)

    assert len(result) == 2
    assert all(p.available for p in result)


@pytest.mark.asyncio
async def test_get_inventory_returns_all(sample_products):
    repo = MockInventoryRepo(sample_products)
    usecase = GetInventoryUseCase(repo)

    result = await usecase.execute(available_only=False)

    assert len(result) == 3
