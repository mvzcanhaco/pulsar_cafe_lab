from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.orm_models import PaymentORM
from app.domain.models.payment import CardType, Payment, PaymentResult
from app.domain.repositories.payment_repository import PaymentRepository


def _to_domain(orm: PaymentORM) -> Payment:
    return Payment(
        id=orm.id,
        order_id=orm.order_id,
        amount_cents=orm.amount_cents,
        tip_amount_cents=orm.tip_amount_cents,
        tax_amount_cents=orm.tax_amount_cents,
        result=PaymentResult(orm.result),
        card_type=CardType(orm.card_type),
        last4=orm.last4,
        nsu=orm.nsu,
        auth_code=orm.auth_code,
        card_brand=orm.card_brand,
        installments=orm.installments,
        merchant_receipt=orm.merchant_receipt,
        customer_receipt=orm.customer_receipt,
        error_message=orm.error_message,
        created_at=orm.created_at,
    )


class SqlPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_payment(self, payment: Payment) -> Payment:
        orm = PaymentORM(
            id=payment.id,
            order_id=payment.order_id,
            amount_cents=payment.amount_cents,
            tip_amount_cents=payment.tip_amount_cents,
            tax_amount_cents=payment.tax_amount_cents,
            result=payment.result.value,
            card_type=payment.card_type.value,
            last4=payment.last4,
            nsu=payment.nsu,
            auth_code=payment.auth_code,
            card_brand=payment.card_brand,
            installments=payment.installments,
            merchant_receipt=payment.merchant_receipt,
            customer_receipt=payment.customer_receipt,
            error_message=payment.error_message,
            created_at=payment.created_at,
        )
        self._session.add(orm)
        await self._session.commit()
        return _to_domain(orm)

    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        orm = await self._session.get(PaymentORM, payment_id)
        return _to_domain(orm) if orm else None

    async def list_payments_for_order(self, order_id: str) -> list[Payment]:
        stmt = select(PaymentORM).where(PaymentORM.order_id == order_id)
        result = await self._session.execute(stmt)
        return [_to_domain(row) for row in result.scalars()]
