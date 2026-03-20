"""
Script para popular o banco de dados com dados de exemplo (café/padaria).
Executar a partir da raiz do projeto:
    python -m scripts.seed_db
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.data.database import AsyncSessionLocal, init_db
from app.data.orm_models import MerchantORM, ProductORM


MERCHANT = MerchantORM(
    id="merchant-pulsar",
    name="Pulsar Café",
    currency="BRL",
    address="Rua das Flores, 100 — São Paulo, SP",
    phone_number="(11) 99999-0000",
    cnpj="00.000.000/0001-00",
)

PRODUCTS = [
    ProductORM(id="cafe-expresso",    name="Café Expresso",      price_cents=500,  category="Café",    description="Expresso curto encorpado"),
    ProductORM(id="cafe-latte",       name="Café Latte",         price_cents=900,  category="Café",    description="Expresso com leite vaporizado"),
    ProductORM(id="cappuccino",       name="Cappuccino",         price_cents=1000, category="Café",    description="Expresso, leite e espuma"),
    ProductORM(id="chocolate-quente", name="Chocolate Quente",   price_cents=1100, category="Bebidas", description="Cacau premium com leite integral"),
    ProductORM(id="suco-laranja",     name="Suco de Laranja",    price_cents=800,  category="Bebidas", description="Natural, 300ml"),
    ProductORM(id="agua-mineral",     name="Água Mineral",       price_cents=300,  category="Bebidas"),
    ProductORM(id="croissant",        name="Croissant Manteiga", price_cents=700,  category="Padaria", description="Folhado de manteiga, assado na hora"),
    ProductORM(id="pao-queijo",       name="Pão de Queijo",      price_cents=400,  category="Padaria", description="Tradicional mineiro, 100g"),
    ProductORM(id="bolo-cenoura",     name="Bolo de Cenoura",    price_cents=600,  category="Padaria", description="Com cobertura de chocolate"),
    ProductORM(id="brigadeiro",       name="Brigadeiro Gourmet", price_cents=350,  category="Doces"),
]


async def seed() -> None:
    await init_db()
    async with AsyncSessionLocal() as session:
        # Merchant
        existing = await session.get(MerchantORM, MERCHANT.id)
        if not existing:
            session.add(MERCHANT)
            print(f"✓ Merchant: {MERCHANT.name}")

        # Products
        for product in PRODUCTS:
            existing = await session.get(ProductORM, product.id)
            if not existing:
                session.add(product)
                print(f"✓ Produto: {product.name} (R$ {product.price_cents/100:.2f})")

        await session.commit()
    print("\nSeed concluído!")


if __name__ == "__main__":
    asyncio.run(seed())
