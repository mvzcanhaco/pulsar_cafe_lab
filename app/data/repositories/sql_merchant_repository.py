from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.orm_models import MerchantORM
from app.domain.models.merchant import Merchant
from app.domain.repositories.merchant_repository import MerchantRepository


def _to_domain(orm: MerchantORM) -> Merchant:
    return Merchant(
        id=orm.id,
        name=orm.name,
        currency=orm.currency,
        address=orm.address,
        phone_number=orm.phone_number,
        cnpj=orm.cnpj,
    )


class SqlMerchantRepository(MerchantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_merchant(self) -> Optional[Merchant]:
        stmt = select(MerchantORM).limit(1)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return _to_domain(orm) if orm else None

    async def save_merchant(self, merchant: Merchant) -> Merchant:
        existing = await self._session.get(MerchantORM, merchant.id)
        if existing:
            existing.name = merchant.name
            existing.currency = merchant.currency
            existing.address = merchant.address
            existing.phone_number = merchant.phone_number
            existing.cnpj = merchant.cnpj
            await self._session.commit()
            return _to_domain(existing)

        orm = MerchantORM(
            id=merchant.id,
            name=merchant.name,
            currency=merchant.currency,
            address=merchant.address,
            phone_number=merchant.phone_number,
            cnpj=merchant.cnpj,
        )
        self._session.add(orm)
        await self._session.commit()
        return _to_domain(orm)
