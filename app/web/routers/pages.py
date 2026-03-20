"""
HTML page routes rendered with Jinja2 templates.
Separate from the JSON API routes (/api/...).
"""
from datetime import datetime
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
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
from app.config import settings
from app.domain.models.payment import PaymentResult
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.payment_repository import PaymentRepository
from app.domain.usecases.create_order import CreateOrderUseCase
from app.domain.usecases.get_inventory import GetInventoryUseCase
from app.domain.usecases.get_merchant import GetMerchantUseCase
from app.domain.usecases.process_payment import ProcessPaymentUseCase

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/web/templates")
logger = logging.getLogger(__name__)


def _build_dashboard_metrics(products, orders):
    now = datetime.now()
    orders_today = [o for o in orders if o.created_at.date() == now.date()]
    total_today_cents = sum(o.total_cents for o in orders_today)
    ticket_medio_cents = int(total_today_cents / len(orders_today)) if orders_today else 0
    carrinho_ativo = len([o for o in orders if o.state.value in {"OPEN", "LOCKED"}])
    fidelidade = min(98, 45 + (len(orders) * 2))
    return {
        "pedidos_hoje": len(orders_today),
        "ticket_medio_cents": ticket_medio_cents,
        "carrinho_ativo": carrinho_ativo,
        "fidelidade_percent": fidelidade,
        "itens_cadastrados": len(products),
        "fila_ao_vivo": carrinho_ativo,
        "campanhas_ativas": 3,
    }


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    inventory: Annotated[GetInventoryUseCase, Depends(get_inventory_usecase)] = None,
    merchant_uc: Annotated[GetMerchantUseCase, Depends(get_merchant_usecase)] = None,
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)] = None,
):
    try:
        products = await inventory.execute()
    except Exception:
        logger.exception("Failed to load products for dashboard")
        products = []

    try:
        merchant = await merchant_uc.execute()
    except Exception:
        logger.exception("Failed to load merchant for dashboard")
        merchant = None

    try:
        orders = await order_repo.list_orders()
    except Exception:
        logger.exception("Failed to load orders for dashboard")
        orders = []

    metrics = _build_dashboard_metrics(products, orders)
    seen: set[str] = set()
    categories = ["Todos"] + [
        p.category for p in products
        if p.category and not (p.category in seen or seen.add(p.category))
    ]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "products": products,
            "merchant": merchant,
            "metrics": metrics,
            "categories": categories,
        },
    )


@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(
    request: Request,
    merchant_uc: Annotated[GetMerchantUseCase, Depends(get_merchant_usecase)] = None,
):
    merchant = await merchant_uc.execute()
    return templates.TemplateResponse(
        "checkout.html",
        {"request": request, "merchant": merchant},
    )


@router.get("/operations", response_class=HTMLResponse)
async def operations_page(
    request: Request,
    merchant_uc: Annotated[GetMerchantUseCase, Depends(get_merchant_usecase)] = None,
):
    merchant = await merchant_uc.execute()
    operations_config = {
        "integration_status": "ONLINE" if settings.fiserv_company_id else "CONFIGURAÇÃO PENDENTE",
        "environment": "SANDBOX" if settings.debug else "PRODUÇÃO",
        "payment_engine": "Fiserv CliSiTef",
        "merchant_name": merchant.name if merchant else "Nao cadastrado",
        "merchant_cnpj": settings.fiserv_merchant_cnpj or (merchant.cnpj if merchant else ""),
        "automation_cnpj": settings.fiserv_company_id,
        "app_id": settings.fiserv_isv_app_id,
        "app_package": "pulsar-cafe-lab-web",
        "app_version": "0.2.0",
        "default_function": "VENDA",
        "operator_timeout_seconds": settings.fiserv_timeout_seconds,
        "sitef_endpoint": f"{settings.fiserv_sitef_ip}:{settings.fiserv_sitef_port}",
    }
    return templates.TemplateResponse(
        "operations.html",
        {"request": request, "ops": operations_config},
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


@router.get("/inventory", response_class=HTMLResponse)
async def inventory_page(
    request: Request,
    inventory_uc: Annotated[GetInventoryUseCase, Depends(get_inventory_usecase)] = None,
):
    products = await inventory_uc.execute()
    critical_items = [p for p in products if p.available and p.price_cents <= 500][:4]
    missing_items = [p for p in products if not p.available][:4]
    return templates.TemplateResponse(
        "inventory.html",
        {
            "request": request,
            "products": products,
            "critical_items": critical_items,
            "missing_items": missing_items,
        },
    )


@router.get("/customers", response_class=HTMLResponse)
async def customers_page(
    request: Request,
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)] = None,
):
    orders = await order_repo.list_orders()
    recurring = max(12, len(orders) * 2)
    campaigns = [
        {"name": "Combo Manhã Pulsar", "reach": "08h–11h"},
        {"name": "Retorno Pós-Almoço", "reach": "14h–17h"},
        {"name": "Clube Espresso", "reach": "Recorrentes"},
    ]
    return templates.TemplateResponse(
        "customers.html",
        {"request": request, "recurring": recurring, "campaigns": campaigns},
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail_page(
    request: Request,
    order_id: str,
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)] = None,
    payment_repo: Annotated[PaymentRepository, Depends(get_payment_repo)] = None,
):
    order = await order_repo.get_order(order_id)
    if not order:
        return HTMLResponse("<h1>Pedido não encontrado</h1>", status_code=404)
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
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON payload"}, status_code=400)

    if not isinstance(body, dict) or not isinstance(body.get("items"), list):
        return JSONResponse({"error": "Payload must include an 'items' list"}, status_code=422)

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
    HTMX endpoint: processes payment and returns an HTML fragment
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
            f'<p class="font-bold text-green-700 text-lg">Pagamento aprovado</p>'
            f'<p class="text-sm text-gray-600 mt-1">NSU: <span class="font-mono">{payment.nsu}</span>'
            f' &bull; Auth: <span class="font-mono">{payment.auth_code}</span></p>'
            f'<p class="text-sm text-gray-600">{payment.card_brand} **** {payment.last4}</p>'
            f"</div>"
        )
    elif payment.result == PaymentResult.CANCEL:
        html = (
            f'<div id="payment-result" class="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">'
            f"Pagamento cancelado pelo usuario.</div>"
        )
    else:
        msg = payment.error_message or "Erro no pagamento"
        html = (
            f'<div id="payment-result" class="mt-3 p-3 bg-red-100 border border-red-200 rounded-lg text-sm text-red-700">'
            f"Falha: {msg}</div>"
        )

    return HTMLResponse(html)

