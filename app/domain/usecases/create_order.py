import uuid
from datetime import datetime

from app.domain.models.order import LineItem, Order, OrderState
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.order_repository import OrderRepository


class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        inventory_repository: InventoryRepository,
    ) -> None:
        self._orders = order_repository
        self._inventory = inventory_repository

    async def execute(self, items: list[dict]) -> Order:
        """
        items: [{"product_id": str, "quantity": int}, ...]
        """
        line_items: list[LineItem] = []
        for item in items:
            quantity_raw = item.get("quantity", 1)
            try:
                quantity = int(quantity_raw)
            except (TypeError, ValueError):
                raise ValueError(f"Invalid quantity for product {item.get('product_id')}: {quantity_raw}")
            if quantity <= 0:
                raise ValueError(f"Quantity must be positive for product {item.get('product_id')}")

            product = await self._inventory.get_product(item["product_id"])
            if product is None:
                raise ValueError(f"Product not found: {item['product_id']}")
            if not product.available:
                raise ValueError(f"Product not available: {product.name}")

            line_items.append(
                LineItem(
                    id=str(uuid.uuid4()),
                    name=product.name,
                    price_cents=product.price_cents,
                    quantity=quantity,
                )
            )

        order = Order(
            id=str(uuid.uuid4()),
            state=OrderState.OPEN,
            line_items=line_items,
            created_at=datetime.now(),
        )
        return await self._orders.create_order(order)
