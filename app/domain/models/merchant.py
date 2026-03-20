from pydantic import BaseModel


class Merchant(BaseModel):
    id: str
    name: str
    currency: str = "BRL"
    address: str = ""
    phone_number: str = ""
    cnpj: str = ""
