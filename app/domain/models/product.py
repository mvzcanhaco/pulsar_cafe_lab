from enum import Enum
from pydantic import BaseModel


class PriceType(str, Enum):
    FIXED = "FIXED"
    VARIABLE = "VARIABLE"
    PER_UNIT = "PER_UNIT"


class Product(BaseModel):
    id: str
    name: str
    price_cents: int  # price in cents (centavos)
    price_type: PriceType = PriceType.FIXED
    available: bool = True
    category: str = ""
    description: str = ""

    @property
    def price_brl(self) -> float:
        return self.price_cents / 100
