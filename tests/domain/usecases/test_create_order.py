import pytest

from app.domain.models.order import Order, OrderState
from app.domain.models.product import Product
from app.domain.usecases.create_order import CreateOrderUseCase


class MockOrderRepo:
    def __init__(self):
        self._orders: dict[str, Order] = {}

    async def list_orders(self, state=None): return list(self._orders.values())
    async def get_order(self, order_id): return self._orders.get(order_id)
    async def create_order(self, order): self._orders[order.id] = order; return order
    async def update_order(self, order): self._orders[order.id] = order; return order


class MockInventoryRepo:
    def __init__(self, products: list[Product]):
        self._products = {p.id: p for p in products}

    async def list_products(self, available_only=True): return list(self._products.values())
    async def get_product(self, product_id): return self._products.get(product_id)
    async def create_product(self, product): return product
    async def update_product(self, product): return product
    async def delete_product(self, product_id): return True


PRODUCTS = [
    Product(id="cafe", name="Café Expresso", price_cents=500, available=True),
    Product(id="agua", name="Água Mineral", price_cents=300, available=True),
    Product(id="inativo", name="Sem Estoque", price_cents=200, available=False),
]


@pytest.mark.asyncio
async def test_create_order_calculates_total():
    order_repo = MockOrderRepo()
    inventory_repo = MockInventoryRepo(PRODUCTS)
    usecase = CreateOrderUseCase(order_repo, inventory_repo)

    order = await usecase.execute([
        {"product_id": "cafe", "quantity": 2},
        {"product_id": "agua", "quantity": 1},
    ])

    assert order.state == OrderState.OPEN
    assert order.total_cents == 1300  # 2×500 + 1×300
    assert len(order.line_items) == 2


@pytest.mark.asyncio
async def test_create_order_raises_for_unknown_product():
    usecase = CreateOrderUseCase(MockOrderRepo(), MockInventoryRepo(PRODUCTS))
    with pytest.raises(ValueError, match="not found"):
        await usecase.execute([{"product_id": "nao-existe", "quantity": 1}])


@pytest.mark.asyncio
async def test_create_order_raises_for_unavailable_product():
    usecase = CreateOrderUseCase(MockOrderRepo(), MockInventoryRepo(PRODUCTS))
    with pytest.raises(ValueError, match="not available"):
        await usecase.execute([{"product_id": "inativo", "quantity": 1}])


@pytest.mark.asyncio
async def test_create_order_raises_for_non_positive_quantity():
    usecase = CreateOrderUseCase(MockOrderRepo(), MockInventoryRepo(PRODUCTS))
    with pytest.raises(ValueError, match="Quantity must be positive"):
        await usecase.execute([{"product_id": "cafe", "quantity": 0}])


@pytest.mark.asyncio
async def test_create_order_raises_for_invalid_quantity_type():
    usecase = CreateOrderUseCase(MockOrderRepo(), MockInventoryRepo(PRODUCTS))
    with pytest.raises(ValueError, match="Invalid quantity"):
        await usecase.execute([{"product_id": "cafe", "quantity": "abc"}])
