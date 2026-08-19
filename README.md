# bag

Shop REST API built with FastAPI and MariaDB.

## Structure

```
meh/
├── docker-compose.yml      # runs MariaDB
├── Makefile
├── pyrightconfig.json
└── app/
    ├── main.py             # entry point
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── .env                # local config (not committed)
    └── bag/                # application package
        ├── database.py     # SQLAlchemy engine and session
        ├── dependencies.py # FastAPI dependencies (db session, auth)
        ├── models.py       # ORM models
        ├── schemas.py      # Pydantic request/response schemas
        ├── settings.py     # pydantic-settings config
        └── routers/
            ├── categories.py
            └── products.py
```

## Setup

**1. Set up the Python environment**

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Configure environment**

Edit `app/.env`:

```ini
DATABASE_URL=mysql+pymysql://app:app@localhost:3306/app
APIKEY=<sha256 hash of your api key>
```

To hash your key:
```bash
echo -n your-api-key-here | sha256sum
```

## Running

```bash
make db      # start MariaDB in Docker
make run     # start the API at http://localhost:8000
make test    # run tests
make db-stop # stop MariaDB
```

Interactive docs available at `http://localhost:8000/docs`.

## Examples

The `examples/` directory contains curl scripts for all category and product CRUD operations. Copy your API key into `examples/.envrc` (see `_envrc.example`) before running them.

## Authentication

Write operations (`POST`, `PATCH`, `DELETE`) require an `X-API-Key` header with the plaintext key:

```
X-API-Key: your-api-key-here
```

Read operations (`GET`) are public. The server hashes the incoming key and compares it to the stored hash in `.env`.

## Endpoints

### Categories

| Method   | Path               | Auth   | Description           |
|----------|--------------------|--------|-----------------------|
| `GET`    | `/categories/`     | public | List all categories   |
| `GET`    | `/categories/{id}` | public | Get a single category |
| `POST`   | `/categories/`     | admin  | Create a category     |
| `PATCH`  | `/categories/{id}` | admin  | Update a category     |
| `DELETE` | `/categories/{id}` | admin  | Delete a category     |

Categories are hierarchical — each category can have an optional parent.

### Products

| Method   | Path              | Auth   | Description                  |
|----------|-------------------|--------|------------------------------|
| `GET`    | `/products/`      | public | List / filter products       |
| `GET`    | `/products/{id}`  | public | Get a single product         |
| `POST`   | `/products/`      | admin  | Create a product             |
| `PATCH`  | `/products/{id}`  | admin  | Update a product             |
| `DELETE` | `/products/{id}`  | admin  | Delete a product             |

If `sku` is omitted on create, one is generated automatically in the format `SKU-000000000`.

### Filtering products

`GET /products/` accepts the following query parameters:

| Parameter     | Description                              |
|---------------|------------------------------------------|
| `q`           | Search in title and description          |
| `sku`         | Partial SKU match                        |
| `min_price`   | Minimum price (inclusive)                |
| `max_price`   | Maximum price (inclusive)                |
| `category_id` | Filter by category                       |
| `has_image`   | `true` / `false` — filter by image presence |

All filters are optional and combinable:

```
GET /products/?q=laptop&min_price=500&has_image=true
```
