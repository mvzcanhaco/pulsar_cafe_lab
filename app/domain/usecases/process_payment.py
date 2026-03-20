from app.domain.models.order import Order, OrderState
from app.domain.models.payment import Payment, PaymentResult
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.payment_repository import PaymentRepository
from app.integrations.fiserv.client import FiservSitefClient
from app.integrations.fiserv.sitef_sale_request import SitefSaleRequest


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

    async def execute(self, order_id: str) -> Payment:
        order = await self._orders.get_order(order_id)
        if order is None:
            raise ValueError(f"Order not found: {order_id}")
        if order.state != OrderState.OPEN:
            raise ValueError(f"Order is not open: {order.state}")
        if not order.line_items:
            raise ValueError("Order has no items")

        request = SitefSaleRequest(
            order_id=order.id,
            amount_cents=order.total_cents,
        )

        payment = await self._fiserv.process_sale(request)

        if payment.result == PaymentResult.SUCCESS:
            order.state = OrderState.PAID
            await self._orders.update_order(order)

        return await self._payments.save_payment(payment)
