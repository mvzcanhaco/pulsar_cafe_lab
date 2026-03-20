"""
HTML page routes — rendered with Jinja2 templates.
Separate from the JSON API routes (/api/...).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import (
    get_create_order_usecase,
    get_inventory_usecase,
    get_merchant_usecase,
    get_order_repo,
    get_payment_repo,
    get_process_payment_usecase,
)
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.payment_repository import PaymentRepository
from app.domain.usecases.create_order import CreateOrderUseCase
from app.domain.usecases.get_inventory import GetInventoryUseCase
from app.domain.usecases.get_merchant import GetMerchantUseCase
from app.domain.usecases.process_payment import ProcessPaymentUseCase
from app.domain.models.payment import PaymentResult

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    inventory: Annotated[GetInventoryUseCase, Depends(get_inventory_usecase)] = None,
    merchant_uc: Annotated[GetMerchantUseCase, Depends(get_merchant_usecase)] = None,
):
    products = await inventory.execute()
    merchant = await merchant_uc.execute()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "products": products, "merchant": merchant},
    )


@router.get("/orders", response_class=HTMLResponse)
async def orders_page(
    request: Request,
    repo: Annotated[OrderRepository, Depends(get_order_repo)] = None,
):
    orders = await repo.list_orders()
    return templates.TemplateResponse(
        "orders.html",
        {"request": request, "orders": orders},
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail_page(
    request: Request,
    order_id: str,
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)] = None,
    payment_repo: Annotated[PaymentRepository, Depends(get_payment_repo)] = None,
):
    order = await order_repo.get_order(order_id)
    payments = await payment_repo.list_payments_for_order(order_id) if order else []
    return templates.TemplateResponse(
        "order_detail.html",
        {"request": request, "order": order, "payments": payments},
    )


@router.post("/orders/new")
async def create_order_web(
    request: Request,
    usecase: Annotated[CreateOrderUseCase, Depends(get_create_order_usecase)] = None,
):
    """Accepts JSON from the frontend cart and returns the new order as JSON."""
    body = await request.json()
    try:
        order = await usecase.execute(items=body.get("items", []))
        return JSONResponse({"id": order.id, "total_cents": order.total_cents})
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=422)


@router.post("/orders/{order_id}/pay", response_class=HTMLResponse)
async def pay_order_htmx(
    request: Request,
    order_id: str,
    usecase: Annotated[ProcessPaymentUseCase, Depends(get_process_payment_usecase)] = None,
):
    """
    HTMX endpoint — processes payment and returns an HTML fragment
    that replaces the payment button in the UI.
    """
    try:
        payment = await usecase.execute(order_id)
    except ValueError as exc:
        return HTMLResponse(
            f'<div id="payment-result" class="mt-3 p-3 bg-red-100 text-red-700 rounded-lg text-sm">'
            f"Erro: {exc}</div>"
        )

    if payment.result == PaymentResult.SUCCESS:
        html = (
            f'<div id="payment-result" class="mt-3 p-4 bg-green-50 border border-green-200 rounded-lg">'
            f'<p class="font-bold text-green-700 text-lg">✅ Pagamento aprovado!</p>'
            f'<p class="text-sm text-gray-600 mt-1">NSU: <span class="font-mono">{payment.nsu}</span>'
            f' &bull; Auth: <span class="font-mono">{payment.auth_code}</span></p>'
            f'<p class="text-sm text-gray-600">{payment.card_brand} **** {payment.last4}</p>'
            f"</div>"
        )
    elif payment.result == PaymentResult.CANCEL:
        html = (
            f'<div id="payment-result" class="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">'
            f"⚠️ Pagamento cancelado pelo usuário.</div>"
        )
    else:
        msg = payment.error_message or "Erro no pagamento"
        html = (
            f'<div id="payment-result" class="mt-3 p-3 bg-red-100 border border-red-200 rounded-lg text-sm text-red-700">'
            f"❌ {msg}</div>"
        )

    return HTMLResponse(html)
