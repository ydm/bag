import hashlib
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from bag.database import SessionLocal
from bag.settings import settings

api_key_header = APIKeyHeader(name="X-API-Key")

ApiKey = Annotated[str, Security(api_key_header)]


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(api_key: ApiKey) -> None:
    hashed = hashlib.sha256(api_key.encode()).hexdigest()
    if hashed != settings.apikey:
        raise HTTPException(status_code=403, detail="Forbidden")


DbSession = Annotated[Session, Depends(get_db)]
AdminAuth = Annotated[None, Depends(require_admin)]
