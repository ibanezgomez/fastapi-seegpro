from pydantic import BaseModel
from typing import List
from datetime import datetime
from schemas.base import PaginationResult, SuccessResponse

### IN/OUT ###

# Base
class TechSchema(BaseModel): # Base model
    id: str
    group: str
    date_created: datetime
    default: bool
class TechSchemaPaginated(PaginationResult): # Base pagination structure
    items: List[TechSchema]

### OUTPUT ###
class TechSchemaResponse(SuccessResponse): # Response one
    data: TechSchema

class TechSchemaListResponse(SuccessResponse): # Response all
    data: List[TechSchema]

class TechSchemaPaginatedResponse(SuccessResponse): # Response pagination
    data: TechSchemaPaginated

### INPUT ###
class TechSchemaCreation(BaseModel): # Request creation
    id: str
    group: str
    default: bool