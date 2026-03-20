"""
Entry point do servidor FastAPI — Pulsar Café Lab.

Inicialização:
    uvicorn app.main:app --reload

Produção:
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routers import inventory, merchant, orders, payments
from app.config import settings
from app.data.database import init_db
from app.data.orm_models import Base  # noqa: F401 — ensures all models are registered
from app.web.routers import pages

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    description="Automação comercial para PDV Fiserv/Clover — servidor web Python",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup() -> None:
    await init_db()


# Static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# REST API routes (prefixed under /api)
api_prefix = "/api/v1"
app.include_router(inventory.router, prefix=api_prefix)
app.include_router(orders.router, prefix=api_prefix)
app.include_router(payments.router, prefix=api_prefix)
app.include_router(merchant.router, prefix=api_prefix)

# Web / HTML routes
app.include_router(pages.router)
