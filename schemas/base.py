from pydantic import BaseModel, Field
from typing import Any, List, Optional

class PaginationResult(BaseModel):
    total_items: int
    total_pages: int
    page: int
    per_page: int
    items: List[Any]

class BaseResponse(BaseModel):
    success: bool = Field(...)
    message: str = Field(...)
    data: Optional[Any]

class SuccessResponse(BaseModel):
    success: bool = Field(True)
    message: str  = Field('OK')
    data:    Optional[Any]

class UnauthorizedResponse(BaseModel):
    success: bool = Field(False)
    message: str  = Field('Unauthorized access')
    data:    Optional[Any]

class ForbiddenResponse(BaseModel):
    success: bool = Field(False)
    message: str  = Field('Forbidden access')
    data:    Optional[Any]

class NotFoundResponse(BaseModel):
    success: bool = Field(False)
    message: str  = Field('Not Found')
    data:    Optional[Any]
    
class IntegrityErrorResponse(BaseModel):
    success: bool = Field(False)
    message: str  = Field('Conflict or Integrity error')
    data:    Optional[Any]

class BadRequestResponse(BaseModel):
    success: bool = Field(False)
    message: str  = Field('Bad Request')
    data:    Optional[Any]

class ServerErrorResponse(BaseModel):
    success: bool = Field(False)
    message: str  = Field('Internal Server Error')
    data:    Optional[Any]

class ServiceUnavailableResponse(BaseModel):
    success: bool = Field(False)
    message: str  = Field('Service Unavailable')
    data:    Optional[Any]

class DeletionResult(BaseModel):
    total_items: int

class DeletionResponse(SuccessResponse):
    data: DeletionResult