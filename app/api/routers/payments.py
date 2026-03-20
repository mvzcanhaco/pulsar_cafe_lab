from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_payment_repo, get_process_payment_usecase
from app.domain.models.payment import Payment
from app.domain.repositories.payment_repository import PaymentRepository
from app.domain.usecases.process_payment import ProcessPaymentUseCase

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{order_id}", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def process_payment(
    order_id: str,
    usecase: Annotated[ProcessPaymentUseCase, Depends(get_process_payment_usecase)],
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
):
    """
    Inicia um pagamento para o pedido via Fiserv Sitef.

    Envie o header `Idempotency-Key` com um UUID único por tentativa de pagamento.
    Requisições repetidas com a mesma chave retornam o pagamento original sem
    reprocessar a transação no terminal.
    """
    try:
        return await usecase.execute(order_id, idempotency_key=idempotency_key)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get("/order/{order_id}", response_model=list[Payment])
async def list_payments_for_order(
    order_id: str,
    repo: Annotated[PaymentRepository, Depends(get_payment_repo)],
):
    return await repo.list_payments_for_order(order_id)


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(
    payment_id: str,
    repo: Annotated[PaymentRepository, Depends(get_payment_repo)],
):
    payment = await repo.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pagamento não encontrado")
    return payment
