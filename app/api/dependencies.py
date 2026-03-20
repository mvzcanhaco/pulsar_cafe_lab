"""
FastAPI dependency injection — wires repositories and use cases.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.data.database import get_db
from app.data.repositories.sql_inventory_repository import SqlInventoryRepository
from app.data.repositories.sql_merchant_repository import SqlMerchantRepository
from app.data.repositories.sql_order_repository import SqlOrderRepository
from app.data.repositories.sql_payment_repository import SqlPaymentRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.merchant_repository import MerchantRepository
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.payment_repository import PaymentRepository
from app.domain.usecases.create_order import CreateOrderUseCase
from app.domain.usecases.get_inventory import GetInventoryUseCase
from app.domain.usecases.get_merchant import GetMerchantUseCase
from app.domain.usecases.process_payment import ProcessPaymentUseCase
from app.integrations.fiserv.client import FiservSitefClient
from app.integrations.fiserv.sitef_sale_config import SitefSaleConfig

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_inventory_repo(session: DbSession) -> InventoryRepository:
    return SqlInventoryRepository(session)


def get_order_repo(session: DbSession) -> OrderRepository:
    return SqlOrderRepository(session)


def get_payment_repo(session: DbSession) -> PaymentRepository:
    return SqlPaymentRepository(session)


def get_merchant_repo(session: DbSession) -> MerchantRepository:
    return SqlMerchantRepository(session)


def get_fiserv_client() -> FiservSitefClient:
    config = SitefSaleConfig(
        sitef_ip=settings.fiserv_sitef_ip,
        sitef_port=settings.fiserv_sitef_port,
        company_id=settings.fiserv_company_id,
        terminal_id=settings.fiserv_terminal_id,
        isv_app_id=settings.fiserv_isv_app_id,
        api_version=settings.fiserv_api_version,
        timeout_seconds=settings.fiserv_timeout_seconds,
    )
    return FiservSitefClient(config)


def get_inventory_usecase(
    repo: Annotated[InventoryRepository, Depends(get_inventory_repo)],
) -> GetInventoryUseCase:
    return GetInventoryUseCase(repo)


def get_merchant_usecase(
    repo: Annotated[MerchantRepository, Depends(get_merchant_repo)],
) -> GetMerchantUseCase:
    return GetMerchantUseCase(repo)


def get_create_order_usecase(
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)],
    inventory_repo: Annotated[InventoryRepository, Depends(get_inventory_repo)],
) -> CreateOrderUseCase:
    return CreateOrderUseCase(order_repo, inventory_repo)


def get_process_payment_usecase(
    order_repo: Annotated[OrderRepository, Depends(get_order_repo)],
    payment_repo: Annotated[PaymentRepository, Depends(get_payment_repo)],
    fiserv: Annotated[FiservSitefClient, Depends(get_fiserv_client)],
) -> ProcessPaymentUseCase:
    return ProcessPaymentUseCase(order_repo, payment_repo, fiserv)
