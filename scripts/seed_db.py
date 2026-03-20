"""
Script para popular o banco de dados com dados de exemplo (café/padaria).
Executar a partir da raiz do projeto:
    python -m scripts.seed_db
"""
import asyncio
import os
import sys

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

# ─────────────────────────────────────────────────────────────
# CATÁLOGO — 8 categorias, ~5-6 itens cada
# ─────────────────────────────────────────────────────────────
PRODUCTS = [

    # ── CAFÉ (bebidas quentes à base de espresso) ─────────────
    ProductORM(
        id="cafe-expresso",
        name="Café Expresso",
        price_cents=500,
        category="Café",
        description="Extração curta e encorpada, blend 100% arábica",
    ),
    ProductORM(
        id="cafe-duplo",
        name="Café Duplo",
        price_cents=700,
        category="Café",
        description="Dois shots de espresso, para os amantes intensos",
    ),
    ProductORM(
        id="cafe-latte",
        name="Café Latte",
        price_cents=900,
        category="Café",
        description="Espresso com leite vaporizado e leve camada de espuma",
    ),
    ProductORM(
        id="cappuccino",
        name="Cappuccino",
        price_cents=1000,
        category="Café",
        description="Espresso, leite vaporizado e espuma densa em proporções iguais",
    ),
    ProductORM(
        id="macchiato",
        name="Macchiato",
        price_cents=750,
        category="Café",
        description="Espresso 'manchado' com uma colherada de leite vaporizado",
    ),
    ProductORM(
        id="flat-white",
        name="Flat White",
        price_cents=1050,
        category="Café",
        description="Espresso duplo com microespuma sedosa — estilo australiano",
    ),
    ProductORM(
        id="affogato",
        name="Affogato",
        price_cents=1400,
        category="Café",
        description="Shot de espresso sobre uma bola de sorvete de creme",
    ),

    # ── CHÁS & INFUSÕES ───────────────────────────────────────
    ProductORM(
        id="cha-verde",
        name="Chá Verde",
        price_cents=650,
        category="Chás & Infusões",
        description="Folhas de chá verde sencha, antioxidante natural",
    ),
    ProductORM(
        id="cha-camomila",
        name="Chá de Camomila",
        price_cents=600,
        category="Chás & Infusões",
        description="Infusão calmante de flores de camomila",
    ),
    ProductORM(
        id="cha-hibisco",
        name="Chá de Hibisco",
        price_cents=650,
        category="Chás & Infusões",
        description="Infusão gelada ou quente de pétalas de hibisco — levemente ácida",
    ),
    ProductORM(
        id="cha-gengibre-limao",
        name="Chá Gengibre & Limão",
        price_cents=700,
        category="Chás & Infusões",
        description="Infusão revigorante com raiz de gengibre e casca de limão",
    ),
    ProductORM(
        id="matcha-latte",
        name="Matcha Latte",
        price_cents=1200,
        category="Chás & Infusões",
        description="Pó de matcha cerimonial japonês com leite vaporizado",
    ),
    ProductORM(
        id="chai-latte",
        name="Chai Latte",
        price_cents=1100,
        category="Chás & Infusões",
        description="Blend de especiarias indianas com leite vaporizado e mel",
    ),

    # ── BEBIDAS FRIAS ─────────────────────────────────────────
    ProductORM(
        id="cold-brew",
        name="Cold Brew",
        price_cents=1100,
        category="Bebidas Frias",
        description="Café extraído a frio por 18h — suave e naturalmente adocicado",
    ),
    ProductORM(
        id="iced-latte",
        name="Iced Latte",
        price_cents=1050,
        category="Bebidas Frias",
        description="Espresso com leite gelado sobre gelo",
    ),
    ProductORM(
        id="smoothie-morango",
        name="Smoothie de Morango",
        price_cents=1300,
        category="Bebidas Frias",
        description="Morangos frescos, iogurte grego e mel — 350ml",
    ),
    ProductORM(
        id="smoothie-mango",
        name="Smoothie de Manga",
        price_cents=1300,
        category="Bebidas Frias",
        description="Manga Haden, coco e toque de cúrcuma — 350ml",
    ),
    ProductORM(
        id="limonada-suica",
        name="Limonada Suíça",
        price_cents=900,
        category="Bebidas Frias",
        description="Limão taiti, leite condensado e creme de leite — 400ml",
    ),
    ProductORM(
        id="agua-mineral",
        name="Água Mineral",
        price_cents=300,
        category="Bebidas Frias",
        description="Garrafa 500ml com ou sem gás",
    ),

    # ── SUCOS NATURAIS ────────────────────────────────────────
    ProductORM(
        id="suco-laranja",
        name="Suco de Laranja",
        price_cents=800,
        category="Sucos",
        description="Espremido na hora, 300ml",
    ),
    ProductORM(
        id="suco-acai",
        name="Suco de Açaí",
        price_cents=1200,
        category="Sucos",
        description="Polpa de açaí com guaraná natural — 350ml",
    ),
    ProductORM(
        id="suco-abacaxi-hortela",
        name="Suco Abacaxi & Hortelã",
        price_cents=900,
        category="Sucos",
        description="Abacaxi pérola com folhas de hortelã frescas — 300ml",
    ),
    ProductORM(
        id="suco-misto-verde",
        name="Suco Verde Detox",
        price_cents=1000,
        category="Sucos",
        description="Couve, pepino, maçã verde, gengibre e limão — 300ml",
    ),
    ProductORM(
        id="suco-maracuja",
        name="Suco de Maracujá",
        price_cents=850,
        category="Sucos",
        description="Maracujá fresco, levemente adoçado — 300ml",
    ),

    # ── PADARIA & SANDUÍCHES ──────────────────────────────────
    ProductORM(
        id="croissant",
        name="Croissant de Manteiga",
        price_cents=700,
        category="Padaria",
        description="Folhado de manteiga importada, assado na hora",
    ),
    ProductORM(
        id="croissant-presunto-queijo",
        name="Croissant Presunto & Queijo",
        price_cents=1100,
        category="Padaria",
        description="Croissant folhado recheado com presunto cozido e queijo gruyère",
    ),
    ProductORM(
        id="pao-queijo",
        name="Pão de Queijo",
        price_cents=400,
        category="Padaria",
        description="Tradicional mineiro, 100g — crocante por fora, macio por dentro",
    ),
    ProductORM(
        id="pao-queijo-grande",
        name="Pão de Queijo Grande",
        price_cents=650,
        category="Padaria",
        description="Pão de queijo artesanal 200g com queijo meia-cura",
    ),
    ProductORM(
        id="sanduiche-presunto",
        name="Sanduíche Natural Frango",
        price_cents=1400,
        category="Padaria",
        description="Pão integral, frango desfiado, cream cheese e cenoura ralada",
    ),
    ProductORM(
        id="sanduiche-gourmet",
        name="Sanduíche Gourmet",
        price_cents=1900,
        category="Padaria",
        description="Ciabatta, rosbife, rúcula, tomate seco e mostarda dijon",
    ),
    ProductORM(
        id="toast-avocado",
        name="Toast de Abacate",
        price_cents=1600,
        category="Padaria",
        description="Pão australiano tostado, abacate temperado, ovo poché e semente de chia",
    ),

    # ── SALGADOS ──────────────────────────────────────────────
    ProductORM(
        id="coxinha",
        name="Coxinha de Frango",
        price_cents=550,
        category="Salgados",
        description="Recheio cremoso de frango desfiado, massa crocante",
    ),
    ProductORM(
        id="esfiha-carne",
        name="Esfiha de Carne",
        price_cents=500,
        category="Salgados",
        description="Massa fofa com recheio de carne moída temperada",
    ),
    ProductORM(
        id="quiche-lorraine",
        name="Quiche Lorraine",
        price_cents=1200,
        category="Salgados",
        description="Massa amanteigada com bacon, queijo e creme de leite",
    ),
    ProductORM(
        id="wrap-vegano",
        name="Wrap Vegano",
        price_cents=1500,
        category="Salgados",
        description="Tortilla integral, húmus, legumes grelhados e mix de folhas",
    ),
    ProductORM(
        id="mini-empada",
        name="Mini Empada",
        price_cents=450,
        category="Salgados",
        description="Massa folhada recheada com palmito e catupiry — unidade",
    ),
    ProductORM(
        id="porcao-salgados",
        name="Porção de Salgados (6 un.)",
        price_cents=2400,
        category="Salgados",
        description="Mix de 6 salgados sortidos: coxinha, empada, esfiha e quibe",
    ),

    # ── BOLOS & TORTAS ────────────────────────────────────────
    ProductORM(
        id="bolo-cenoura",
        name="Fatia Bolo de Cenoura",
        price_cents=700,
        category="Bolos & Tortas",
        description="Bolo fofinho com cobertura de ganache de chocolate",
    ),
    ProductORM(
        id="bolo-limao",
        name="Fatia Bolo de Limão",
        price_cents=700,
        category="Bolos & Tortas",
        description="Bolo com calda de limão e cobertura de merengue",
    ),
    ProductORM(
        id="torta-maracuja",
        name="Fatia Torta de Maracujá",
        price_cents=900,
        category="Bolos & Tortas",
        description="Base de biscoito, mousse de maracujá e geleia de frutas",
    ),
    ProductORM(
        id="cheesecake-frutas",
        name="Cheesecake de Frutas Vermelhas",
        price_cents=1100,
        category="Bolos & Tortas",
        description="Cream cheese sobre base de biscoito, calda de frutas vermelhas",
    ),
    ProductORM(
        id="brownie",
        name="Brownie de Chocolate",
        price_cents=800,
        category="Bolos & Tortas",
        description="Brownie denso com chocolate 70% cacau e nozes",
    ),
    ProductORM(
        id="cookie",
        name="Cookie Artesanal",
        price_cents=550,
        category="Bolos & Tortas",
        description="Cookie crocante nas bordas, macio no centro — gotas de chocolate",
    ),

    # ── DOCES & CONFEITARIA ───────────────────────────────────
    ProductORM(
        id="brigadeiro",
        name="Brigadeiro Gourmet",
        price_cents=350,
        category="Doces",
        description="Brigadeiro tradicional com granulado belga — unidade",
    ),
    ProductORM(
        id="brigadeiro-pistache",
        name="Brigadeiro de Pistache",
        price_cents=450,
        category="Doces",
        description="Brigadeiro branco com pistache triturado e flor de sal",
    ),
    ProductORM(
        id="trufa-chocolate",
        name="Trufa de Chocolate",
        price_cents=500,
        category="Doces",
        description="Ganache de chocolate belga 60% cacau, cacau em pó",
    ),
    ProductORM(
        id="macaron",
        name="Macaron",
        price_cents=600,
        category="Doces",
        description="Macaron francês — sabores: baunilha, framboesa ou pistache",
    ),
    ProductORM(
        id="beijinho",
        name="Beijinho de Coco",
        price_cents=350,
        category="Doces",
        description="Doce de leite condensado com coco ralado — unidade",
    ),
    ProductORM(
        id="caixa-mix-doces",
        name="Caixinha Mix de Doces (6 un.)",
        price_cents=2200,
        category="Doces",
        description="Seleção de 6 doces gourmet: 2 brigadeiros, 2 trufas, 1 macaron, 1 beijinho",
    ),
]


async def seed() -> None:
    await init_db()
    async with AsyncSessionLocal() as session:
        # Merchant
        existing = await session.get(MerchantORM, MERCHANT.id)
        if not existing:
            session.add(MERCHANT)
            print(f"✓ Merchant: {MERCHANT.name}")

        # Products por categoria
        categories: dict[str, list[str]] = {}
        added = 0
        for product in PRODUCTS:
            existing = await session.get(ProductORM, product.id)
            if not existing:
                session.add(product)
                added += 1
            categories.setdefault(product.category, []).append(product.name)

        await session.commit()

    print("\n-- Catalogo --")
    for cat, names in categories.items():
        print(f"\n  {cat} ({len(names)} produtos)")
        for n in names:
            print(f"    - {n}")
    print(f"\n[OK] {added} produto(s) novo(s) inserido(s). Total: {len(PRODUCTS)} produtos em {len(categories)} categorias.")


if __name__ == "__main__":
    asyncio.run(seed())
