from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None


class CategoryResponse(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None


class ProductCreate(BaseModel):
    title: str
    description: str
    image: str | None = None
    sku: str | None = None
    price: Decimal
    category_id: int


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    image: str | None = None
    sku: str | None = None
    price: Decimal | None = None
    category_id: int | None = None


class ProductResponse(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    image: str | None
    sku: str
    price: Decimal
    category_id: int
