import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.orm_models import ProductORM
from app.domain.models.product import PriceType, Product
from app.domain.repositories.inventory_repository import InventoryRepository


def _to_domain(orm: ProductORM) -> Product:
    return Product(
        id=orm.id,
        name=orm.name,
        price_cents=orm.price_cents,
        price_type=PriceType(orm.price_type),
        available=orm.available,
        category=orm.category,
        description=orm.description,
    )


def _to_orm(product: Product) -> ProductORM:
    return ProductORM(
        id=product.id or str(uuid.uuid4()),
        name=product.name,
        price_cents=product.price_cents,
        price_type=product.price_type.value,
        available=product.available,
        category=product.category,
        description=product.description,
    )


class SqlInventoryRepository(InventoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_products(self, available_only: bool = True) -> list[Product]:
        stmt = select(ProductORM)
        if available_only:
            stmt = stmt.where(ProductORM.available.is_(True))
        result = await self._session.execute(stmt)
        return [_to_domain(row) for row in result.scalars()]

    async def get_product(self, product_id: str) -> Optional[Product]:
        result = await self._session.get(ProductORM, product_id)
        return _to_domain(result) if result else None

    async def create_product(self, product: Product) -> Product:
        if not product.id:
            product = product.model_copy(update={"id": str(uuid.uuid4())})
        orm = _to_orm(product)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _to_domain(orm)

    async def update_product(self, product: Product) -> Product:
        orm = await self._session.get(ProductORM, product.id)
        if orm is None:
            raise ValueError(f"Product not found: {product.id}")
        orm.name = product.name
        orm.price_cents = product.price_cents
        orm.price_type = product.price_type.value
        orm.available = product.available
        orm.category = product.category
        orm.description = product.description
        await self._session.commit()
        return _to_domain(orm)

    async def delete_product(self, product_id: str) -> bool:
        orm = await self._session.get(ProductORM, product_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.commit()
        return True
