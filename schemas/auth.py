from pydantic import BaseModel
from typing import Any, Dict
from utils.enums import AuthStatus
from datetime import datetime
from schemas.user import UserSchema

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class UserSessionSchema(BaseModel):
    user: UserSchema | None
    expires_at: datetime | None
    status: AuthStatus
    errors: Dict[str, Any]