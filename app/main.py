"""
Entry point do servidor FastAPI - Pulsar Cafe Lab.

Inicializacao:
    uvicorn app.main:app --reload

Producao:
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import logging
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.api.routers import inventory, merchant, orders, payments
from app.config import settings
from app.data.database import init_db
from app.data.orm_models import Base  # noqa: F401 - ensures all models are registered
from app.web.routers import pages

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.runtime")

app = FastAPI(
    title=settings.app_name,
    description="Automacao comercial para PDV Fiserv/Clover - servidor web Python",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug,
)


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    logger.info("Startup complete. cwd=%s", Path.cwd())


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


@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "cwd": str(Path.cwd()),
        "debug": settings.debug,
        "runtime_log": str(Path.cwd() / "runtime-errors.log"),
    }


@app.middleware("http")
async def capture_unhandled_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:  # pragma: no cover - defensive boundary
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        logger.error("Unhandled exception on %s %s\n%s", request.method, request.url.path, tb)
        with Path("runtime-errors.log").open("a", encoding="utf-8") as fp:
            fp.write(f"{request.method} {request.url.path}\n{tb}\n")
        if settings.debug:
            return PlainTextResponse(tb, status_code=500)
        return PlainTextResponse("Internal Server Error", status_code=500)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error("Unhandled exception (handler) on %s %s\n%s", request.method, request.url.path, tb)
    with Path("runtime-errors.log").open("a", encoding="utf-8") as fp:
        fp.write(f"{request.method} {request.url.path}\n{tb}\n")
    if settings.debug:
        return PlainTextResponse(tb, status_code=500)
    return PlainTextResponse("Internal Server Error", status_code=500)
