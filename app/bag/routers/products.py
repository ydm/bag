import secrets
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_

from bag.dependencies import AdminAuth, DbSession
from bag.models import Product
from bag.schemas import ProductCreate, ProductResponse, ProductUpdate


def generate_sku() -> str:
    return f"SKU-{secrets.randbelow(10**9):09d}"


router = APIRouter(prefix="/products", tags=["products"])


class ProductFilter:
    q: str | None
    sku: str | None
    min_price: Decimal | None
    max_price: Decimal | None
    category_id: int | None
    has_image: bool | None

    def __init__(
        self,
        q: Annotated[
            str | None, Query(description="Search in title and description")
        ] = None,
        sku: Annotated[str | None, Query(description="Partial SKU match")] = None,
        min_price: Annotated[Decimal | None, Query()] = None,
        max_price: Annotated[Decimal | None, Query()] = None,
        category_id: Annotated[int | None, Query()] = None,
        has_image: Annotated[bool | None, Query()] = None,
    ):
        self.q = q
        self.sku = sku
        self.min_price = min_price
        self.max_price = max_price
        self.category_id = category_id
        self.has_image = has_image


ProductFilters = Annotated[ProductFilter, Depends()]


@router.get("/", response_model=list[ProductResponse])
def list_products(db: DbSession, filters: ProductFilters):
    query = db.query(Product)
    if filters.q:
        query = query.filter(
            or_(
                Product.title.ilike(f"%{filters.q}%"),
                Product.description.ilike(f"%{filters.q}%"),
            )
        )
    if filters.sku:
        query = query.filter(Product.sku.ilike(f"%{filters.sku}%"))
    if filters.min_price is not None:
        query = query.filter(Product.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(Product.price <= filters.max_price)
    if filters.category_id is not None:
        query = query.filter(Product.category_id == filters.category_id)
    if filters.has_image is not None:
        query = query.filter(
            Product.image.is_not(None) if filters.has_image else Product.image.is_(None)
        )
    return query.all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: DbSession):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: DbSession, _: AdminAuth):
    dump = data.model_dump()
    dump["sku"] = dump["sku"] or generate_sku()
    product = Product(**dump)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: DbSession, _: AdminAuth):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in data.model_dump(exclude_unset=True).items():  # pyright: ignore[reportAny]
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: DbSession, _: AdminAuth):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
