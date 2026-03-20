from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_merchant_repo, get_merchant_usecase
from app.domain.models.merchant import Merchant
from app.domain.repositories.merchant_repository import MerchantRepository
from app.domain.usecases.get_merchant import GetMerchantUseCase

router = APIRouter(prefix="/merchant", tags=["merchant"])


@router.get("", response_model=Merchant | None)
async def get_merchant(
    usecase: Annotated[GetMerchantUseCase, Depends(get_merchant_usecase)] = None,
):
    return await usecase.execute()


@router.put("", response_model=Merchant)
async def save_merchant(
    merchant: Merchant,
    repo: Annotated[MerchantRepository, Depends(get_merchant_repo)] = None,
):
    return await repo.save_merchant(merchant)
