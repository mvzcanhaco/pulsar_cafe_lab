from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.merchant import Merchant


class MerchantRepository(ABC):
    @abstractmethod
    async def get_merchant(self) -> Optional[Merchant]:
        ...

    @abstractmethod
    async def save_merchant(self, merchant: Merchant) -> Merchant:
        ...
