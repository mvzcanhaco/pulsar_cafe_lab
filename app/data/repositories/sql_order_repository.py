import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data.orm_models import LineItemORM, OrderORM
from app.domain.models.order import LineItem, Order, OrderState
from app.domain.repositories.order_repository import OrderRepository

logger = logging.getLogger(__name__)


def _safe_order_state(value: str) -> OrderState:
    try:
        return OrderState(value)
    except ValueError:
        logger.warning("Unknown order state '%s' in database. Falling back to OPEN.", value)
        return OrderState.OPEN


def _to_domain(orm: OrderORM) -> Order:
    return Order(
        id=orm.id,
        state=_safe_order_state(orm.state),
        note=orm.note,
        currency=orm.currency,
        merchant_id=orm.merchant_id,
        created_at=orm.created_at,
        line_items=[
            LineItem(
                id=li.id,
                name=li.name,
                price_cents=li.price_cents,
                quantity=li.quantity,
            )
            for li in orm.line_items
        ],
    )


class SqlOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(self, state: Optional[OrderState] = None) -> list[Order]:
        stmt = select(OrderORM).options(selectinload(OrderORM.line_items))
        if state:
            stmt = stmt.where(OrderORM.state == state.value)
        result = await self._session.execute(stmt)
        return [_to_domain(row) for row in result.scalars()]

    async def get_order(self, order_id: str) -> Optional[Order]:
        stmt = (
            select(OrderORM)
            .where(OrderORM.id == order_id)
            .options(selectinload(OrderORM.line_items))
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _to_domain(orm) if orm else None

    async def create_order(self, order: Order) -> Order:
        orm = OrderORM(
            id=order.id or str(uuid.uuid4()),
            state=order.state.value,
            note=order.note,
            currency=order.currency,
            merchant_id=order.merchant_id,
            created_at=order.created_at,
            line_items=[
                LineItemORM(
                    id=li.id,
                    name=li.name,
                    price_cents=li.price_cents,
                    quantity=li.quantity,
                )
                for li in order.line_items
            ],
        )
        self._session.add(orm)
        await self._session.commit()
        return await self.get_order(orm.id)

    async def update_order(self, order: Order) -> Order:
        orm = await self._session.get(OrderORM, order.id)
        if orm is None:
            raise ValueError(f"Order not found: {order.id}")
        orm.state = order.state.value
        orm.note = order.note
        await self._session.commit()
        return await self.get_order(orm.id)
