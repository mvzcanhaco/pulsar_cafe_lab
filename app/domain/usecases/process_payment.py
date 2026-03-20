import logging
from typing import Optional

from app.domain.models.order import Order, OrderState, InvalidStateTransition
from app.domain.models.payment import Payment, PaymentResult
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.payment_repository import PaymentRepository
from app.integrations.fiserv.client import FiservSitefClient
from app.integrations.fiserv.sitef_sale_request import SitefSaleRequest

logger = logging.getLogger(__name__)


class ProcessPaymentUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        payment_repository: PaymentRepository,
        fiserv_client: FiservSitefClient,
    ) -> None:
        self._orders = order_repository
        self._payments = payment_repository
        self._fiserv = fiserv_client

    async def execute(self, order_id: str, idempotency_key: Optional[str] = None) -> Payment:
        # Idempotência: retorna pagamento existente se a mesma chave já foi processada
        if idempotency_key:
            existing = await self._payments.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                logger.info(
                    "Idempotent payment returned for key=%s order=%s",
                    idempotency_key,
                    order_id,
                )
                return existing

        order = await self._orders.get_order(order_id)
        if order is None:
            raise ValueError(f"Pedido não encontrado: {order_id}")
        if not order.line_items:
            raise ValueError("Pedido não possui itens")

        # Trava o pedido via state machine antes de enviar ao Sitef
        try:
            order.transition_to(OrderState.LOCKED)
        except InvalidStateTransition as exc:
            raise ValueError(str(exc)) from exc
        await self._orders.update_order(order)

        request = SitefSaleRequest(
            order_id=order.id,
            amount_cents=order.total_cents,
        )

        payment = await self._fiserv.process_sale(request)
        payment = payment.model_copy(update={"idempotency_key": idempotency_key})

        # Transição final via state machine
        try:
            if payment.result == PaymentResult.SUCCESS:
                order.transition_to(OrderState.PAID)
            else:
                # Falha: destrava o pedido para nova tentativa
                order.transition_to(OrderState.OPEN)
        except InvalidStateTransition as exc:
            logger.error("State machine error after payment: %s", exc)

        await self._orders.update_order(order)
        return await self._payments.save_payment(payment)
