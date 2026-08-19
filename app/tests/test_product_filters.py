from collections.abc import Generator, Sized
from decimal import Decimal
from typing import Any

import pytest
from bag.database import Base
from bag.dependencies import get_db
from bag.models import Category, Product
from fastapi.testclient import TestClient
from httpx2 import Response
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)


def assert_length(xs: Any, expected: int) -> None:  # pyright: ignore[reportAny, reportExplicitAny]
    assert isinstance(xs, Sized)
    assert len(xs) == expected


def assert_titles(xs: Any, expected: set[str]) -> None:  # pyright: ignore[reportAny, reportExplicitAny]
    assert_length(xs, len(expected))
    assert isinstance(xs, list)
    assert {x["title"] for x in xs} == expected  # pyright: ignore[reportUnknownVariableType]


@pytest.fixture(scope="session", autouse=True)
def create_tables() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="session")
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def category(db: Session) -> Category:
    cat = Category(name="Electronics")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@pytest.fixture(scope="session")
def products(db: Session, category: Category) -> list[Product]:
    items = [
        Product(
            title="Laptop",
            description="Powerful laptop for professionals",
            sku="SKU-001",
            price=Decimal("999.99"),
            category_id=category.id,
            image="https://example.com/laptop.jpg",
        ),
        Product(
            title="Mouse",
            description="Wireless mouse with ergonomic design",
            sku="SKU-002",
            price=Decimal("29.99"),
            category_id=category.id,
            image=None,
        ),
        Product(
            title="Keyboard",
            description="Mechanical keyboard with RGB lighting",
            sku="SKU-003",
            price=Decimal("79.99"),
            category_id=category.id,
            image="https://example.com/keyboard.jpg",
        ),
        Product(
            title="Monitor",
            description="4K display with HDR support",
            sku="SKU-004",
            price=Decimal("499.99"),
            category_id=category.id,
            image=None,
        ),
    ]
    db.add_all(items)
    db.commit()
    for item in items:
        db.refresh(item)
    return items


@pytest.fixture(autouse=True)
def require_products(products: list[Product]) -> None:  # pyright: ignore[reportUnusedParameter]
    pass


def test_no_filters_returns_all(client: TestClient, products: list[Product]):
    response: Response = client.get("/products/")
    assert response.status_code == 200
    assert_length(response.json(), len(products))


def test_q_matches_title(client: TestClient):
    response: Response = client.get("/products/?q=laptop")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_length(data, 1)
    assert data[0]["title"] == "Laptop"


def test_q_matches_description(client: TestClient):
    response: Response = client.get("/products/?q=wireless")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_length(data, 1)
    assert data[0]["title"] == "Mouse"


def test_q_is_case_insensitive(client: TestClient):
    response: Response = client.get("/products/?q=LAPTOP")
    assert response.status_code == 200
    assert_length(response.json(), 1)


def test_q_no_match(client: TestClient):
    response: Response = client.get("/products/?q=zzznomatch")
    assert response.status_code == 200
    assert response.json() == []


def test_sku_partial_match(client: TestClient):
    response: Response = client.get("/products/?sku=SKU-00")
    assert response.status_code == 200
    assert_length(response.json(), 4)


def test_sku_exact_match(client: TestClient):
    response: Response = client.get("/products/?sku=SKU-001")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_length(data, 1)
    assert data[0]["sku"] == "SKU-001"


def test_min_price(client: TestClient):
    response: Response = client.get("/products/?min_price=100")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_titles(data, {"Laptop", "Monitor"})


def test_max_price(client: TestClient):
    response: Response = client.get("/products/?max_price=50")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_titles(data, {"Mouse"})


def test_price_range(client: TestClient):
    response: Response = client.get("/products/?min_price=50&max_price=500")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_titles(data, {"Keyboard", "Monitor"})


def test_price_range_inclusive(client: TestClient):
    response: Response = client.get("/products/?min_price=29.99&max_price=29.99")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_length(data, 1)
    assert data[0]["title"] == "Mouse"


def test_category_filter(client: TestClient, category: Category):
    response: Response = client.get(f"/products/?category_id={category.id}")
    assert response.status_code == 200
    assert_length(response.json(), 4)


def test_category_filter_no_match(client: TestClient):
    response: Response = client.get("/products/?category_id=99999")
    assert response.status_code == 200
    assert_length(response.json(), 0)


def test_has_image_true(client: TestClient):
    response: Response = client.get("/products/?has_image=true")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_titles(data, {"Laptop", "Keyboard"})


def test_has_image_false(client: TestClient):
    response: Response = client.get("/products/?has_image=false")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_titles(data, {"Mouse", "Monitor"})


def test_combined_q_and_has_image(client: TestClient):
    response: Response = client.get("/products/?q=keyboard&has_image=true")
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_length(data, 1)
    assert data[0]["title"] == "Keyboard"


def test_combined_price_range_and_has_image(client: TestClient):
    response: Response = client.get(
        "/products/?min_price=50&max_price=500&has_image=true"
    )
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_titles(data, {"Keyboard"})


def test_combined_category_and_price(client: TestClient, category: Category):
    response: Response = client.get(
        f"/products/?category_id={category.id}&max_price=100"
    )
    data: Any = response.json()  # pyright: ignore[reportAny, reportExplicitAny]
    assert response.status_code == 200
    assert_titles(data, {"Mouse", "Keyboard"})
