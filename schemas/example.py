from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from schemas.base import PaginationResult, SuccessResponse

### IN/OUT ###

# Base
class ExampleSchema(BaseModel): # Base model
    id: int
    name: str
    date_created: datetime
    description: str | None
    active: bool
    
class ExampleSchemaPaginated(PaginationResult): # Base pagination structure
    items: List[ExampleSchema]

### OUTPUT ###
class ExampleSchemaResponse(SuccessResponse): # Response one
    data: ExampleSchema

class ExampleSchemaListResponse(SuccessResponse): # Response all
    data: List[ExampleSchema]

class ExampleSchemaPaginatedResponse(SuccessResponse): # Response pagination
    data: ExampleSchemaPaginated

### INPUT ###
class ExampleSchemaCreation(BaseModel): # Request creation
    name: str
    description: str | None = Field(default=None)
    active: bool | None = Field(default=True)

class ExampleSchemaPartialUpdate(BaseModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    active: bool | None = Field(default=True)