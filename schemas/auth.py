from pydantic import BaseModel
from typing import Dict, Any
from utils.enums import AuthStatus
from datetime import date, datetime

class CreateClientSchema(BaseModel):
    id: str
    desc: str
    permissions: Dict[str, Any]
    password: str

class ClientSchema(BaseModel):
    id: str
    desc: str
    provider: str
    date_created: datetime | None = None
    permissions: Dict[str, Any]
    hashed_password: str | None = None

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class ClientSessionSchema(BaseModel):
    client: ClientSchema | None
    expires_at: datetime | None
    status: AuthStatus
    errors: Dict[str, Any]