from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import get_create_order_usecase, get_order_repo
from app.domain.models.order import Order, OrderState
from app.domain.repositories.order_repository import OrderRepository
from app.domain.usecases.create_order import CreateOrderUseCase

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderItemInput(BaseModel):
    product_id: str
    quantity: int = Field(default=1, gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemInput]
    note: str = ""


@router.get("", response_model=list[Order])
async def list_orders(
    state: Optional[OrderState] = None,
    repo: Annotated[OrderRepository, Depends(get_order_repo)] = None,
):
    return await repo.list_orders(state=state)


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    repo: Annotated[OrderRepository, Depends(get_order_repo)] = None,
):
    order = await repo.get_order(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    usecase: Annotated[CreateOrderUseCase, Depends(get_create_order_usecase)] = None,
):
    try:
        return await usecase.execute(
            items=[item.model_dump() for item in body.items]
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
