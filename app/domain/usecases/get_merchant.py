from typing import Optional

from app.domain.models.merchant import Merchant
from app.domain.repositories.merchant_repository import MerchantRepository


class GetMerchantUseCase:
    def __init__(self, repository: MerchantRepository) -> None:
        self._repo = repository

    async def execute(self) -> Optional[Merchant]:
        return await self._repo.get_merchant()
