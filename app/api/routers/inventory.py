from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_inventory_repo, get_inventory_usecase
from app.domain.models.product import PriceType, Product
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.usecases.get_inventory import GetInventoryUseCase

router = APIRouter(prefix="/inventory", tags=["inventory"])


class ProductCreate(BaseModel):
    name: str
    price_cents: int
    price_type: PriceType = PriceType.FIXED
    available: bool = True
    category: str = ""
    description: str = ""


@router.get("/products", response_model=list[Product])
async def list_products(
    available_only: bool = True,
    usecase: Annotated[GetInventoryUseCase, Depends(get_inventory_usecase)] = None,
):
    return await usecase.execute(available_only=available_only)


@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    repo: Annotated[InventoryRepository, Depends(get_inventory_repo)] = None,
):
    product = await repo.get_product(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    body: ProductCreate,
    repo: Annotated[InventoryRepository, Depends(get_inventory_repo)] = None,
):
    import uuid
    product = Product(id=str(uuid.uuid4()), **body.model_dump())
    return await repo.create_product(product)


@router.patch("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    body: ProductCreate,
    repo: Annotated[InventoryRepository, Depends(get_inventory_repo)] = None,
):
    existing = await repo.get_product(product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    updated = existing.model_copy(update=body.model_dump())
    return await repo.update_product(updated)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    repo: Annotated[InventoryRepository, Depends(get_inventory_repo)] = None,
):
    deleted = await repo.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
