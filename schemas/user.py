from pydantic import BaseModel
from typing import List
from datetime import datetime
from schemas.base import PaginationResult, SuccessResponse

### IN/OUT ###

# Base
class UserSchema(BaseModel):
    id: str
    name: str
    surname: str
    roles: List[str]
    date_created: datetime | None = None
    
class UserSchemaPaginated(PaginationResult): # Base pagination structure
    items: List[UserSchema]

### OUTPUT ###
class UserSchemaResponse(SuccessResponse): # Response one
    data: UserSchema

class UserSchemaListResponse(SuccessResponse): # Response all
    data: List[UserSchema]

class UserSchemaPaginatedResponse(SuccessResponse): # Response pagination
    data: UserSchemaPaginated

### INPUT ###

class CreateUserSchema(BaseModel):
    id: str
    name: str
    surname: str
    roles: List[str]
    password: str
