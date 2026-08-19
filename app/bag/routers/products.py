import secrets

from fastapi import APIRouter, HTTPException

from bag.dependencies import AdminAuth, DbSession
from bag.models import Product
from bag.schemas import ProductCreate, ProductResponse, ProductUpdate


def generate_sku() -> str:
    return f"SKU-{secrets.randbelow(10 ** 9):09d}"

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
def list_products(db: DbSession):
    return db.query(Product).all()


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
