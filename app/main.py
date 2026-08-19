from contextlib import asynccontextmanager

import bag.models  # noqa: F401  # pyright: ignore[reportUnusedImport]
from bag.database import Base, engine
from bag.routers.categories import router as categories_router
from bag.routers.products import router as products_router
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(categories_router)
app.include_router(products_router)
