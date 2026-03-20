# Pulsar Café Lab — Guia para Claude

## O que é este projeto
Servidor web Python para automação comercial de PDV, integrado com a API Fiserv/Sitef.
Espelha a lógica do app Android (`../clover-dev-setup/clover-app-template/`) porém como servidor web,
permitindo enviar transações para terminais POS Clover remotamente.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| API REST | FastAPI + Pydantic v2 |
| Servidor | Uvicorn (ASGI) |
| ORM | SQLAlchemy 2 (async) |
| Banco (dev) | SQLite via aiosqlite |
| Banco (prod) | PostgreSQL via asyncpg |
| Web UI | Jinja2 + HTMX + Tailwind CSS |
| Integração POS | HTTPX → Fiserv CliSiTef |
| Testes | pytest + pytest-asyncio |

## Arquitetura (Clean Architecture)
```
app/
├── domain/         # puro Python — sem dependências de framework
│   ├── models/     # Pydantic domain models (Product, Order, Payment, Merchant)
│   ├── repositories/  # interfaces abstratas (ABC)
│   └── usecases/   # regras de negócio
├── data/           # implementações concretas das interfaces de domínio
│   ├── orm_models.py   # SQLAlchemy ORM (separado dos modelos de domínio)
│   └── repositories/   # SqlXxxRepository
├── api/            # routers FastAPI JSON (/api/v1/...)
├── integrations/
│   └── fiserv/     # cliente Sitef + parser de resultados
└── web/            # routers HTML + templates Jinja2
```

## Regras críticas

### Fiserv / Sitef
- Todos os valores monetários são em **centavos** (inteiros). Nunca use float para dinheiro.
- O CliSiTef precisa estar rodando localmente na porta 4096 (configurável via `.env`)
- Mapeamento de códigos de resposta está em `app/integrations/fiserv/sitef_result_parser.py`
- `FISERV_COMPANY_ID` = CNPJ da empresa (14 dígitos, sem formatação)
- `FISERV_TERMINAL_ID` = ID do terminal PDV no Sitef

### Banco de dados
- Use `aiosqlite` para desenvolvimento e `asyncpg` para produção
- Nunca chame operações de banco fora de uma `AsyncSession`
- Modelos ORM ficam em `app/data/orm_models.py` — NÃO nos modelos de domínio

### API
- REST JSON: prefixo `/api/v1/`
- Páginas HTML: sem prefixo (`/`, `/orders`, etc.)
- Endpoints HTMX retornam fragmentos HTML, não JSON

## Comandos úteis

```bash
# Instalar dependências
pip install -r requirements.txt

# Popular banco com dados de exemplo
python -m scripts.seed_db

# Rodar servidor de desenvolvimento
uvicorn app.main:app --reload

# Rodar testes
pytest

# Rodar com cobertura
pytest --cov=app --cov-report=term-missing
```

## Variáveis de ambiente
Copie `.env.example` para `.env` e preencha os valores da Fiserv.
A aplicação usa `pydantic-settings` para carregar o `.env` automaticamente.

## Referência Android
O app base está em `../clover-dev-setup/clover-app-template/`.
Correspondência entre os módulos:

| Android (Kotlin) | Python |
|---|---|
| `SitefSaleConfig.kt` | `app/integrations/fiserv/sitef_sale_config.py` |
| `SitefSaleRequest.kt` | `app/integrations/fiserv/sitef_sale_request.py` |
| `SitefSaleResultParser.kt` | `app/integrations/fiserv/sitef_result_parser.py` |
| `CloverInventoryRepository.kt` | `app/data/repositories/sql_inventory_repository.py` |
| `CloverOrderRepository.kt` | `app/data/repositories/sql_order_repository.py` |
| `CloverPaymentRepository.kt` | `app/data/repositories/sql_payment_repository.py` |
| `ProcessPaymentUseCase.kt` | `app/domain/usecases/process_payment.py` |
