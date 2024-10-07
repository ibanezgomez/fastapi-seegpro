from sqlalchemy import select
from models.example import ExampleModel
from schemas.base import PaginationResult, DeletionResult, DeletionResponse
from schemas.example import *
from services.base import BaseDataManager, BaseService

class ExampleService(BaseService):

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def get_example(self, id: int) -> ExampleSchemaResponse:
        """Get example by ID."""
        return ExampleDataManager(self.session).get_example(id=id).to_schema_response(ExampleSchemaResponse)

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    @BaseService.FilterValidator
    def get_examples(self, page: int, per_page: int, filters: List[dict])-> ExampleSchemaPaginatedResponse:
        """Get examples paginated."""
        result = ExampleDataManager(self.session).get_examples(page, per_page, filters)
        result.items=self.getSchemasFromModels(result.items, ExampleSchema)
        return ExampleSchemaPaginatedResponse(data=result.model_dump())

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def create_example(self, data: ExampleSchemaCreation) -> ExampleSchemaResponse:
        """Create an example."""
        return ExampleDataManager(self.session).create_example(data).to_schema_response(ExampleSchemaResponse)
    
    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def delete_example(self, id: int) -> ExampleSchemaResponse:
        return ExampleDataManager(self.session).delete_example(id).to_schema_response(ExampleSchemaResponse)

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def delete_examples(self) -> ExampleSchemaResponse:
        result = ExampleDataManager(self.session).delete_examples()
        return DeletionResponse(data=result.model_dump())

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def update_full_example(self, id: int, data: ExampleSchemaCreation) -> ExampleSchemaResponse:
        return ExampleDataManager(self.session).update_full_example(id, data).to_schema_response(ExampleSchemaResponse)

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def update_partial_example(self, id: int, data: ExampleSchemaPartialUpdate) -> ExampleSchemaResponse:
        return ExampleDataManager(self.session).update_partial_example(id, data).to_schema_response(ExampleSchemaResponse)

class ExampleDataManager(BaseDataManager):
   
    def get_example(self, **kwargs) -> ExampleModel:
        return self.basic_get_one(ExampleModel, kwargs)
    
    def get_examples(self, page: int, per_page: int, filters: List[dict]) -> PaginationResult:       
        return self.get_paginated(ExampleModel, page=page, per_page=per_page, filters=filters)

    def create_example(self, data: ExampleSchemaCreation) -> ExampleModel:
        return self.basic_create_one(ExampleModel, data)

    def delete_example(self, id: int) -> ExampleModel:
        return self.basic_delete_one(ExampleModel, id)

    def delete_examples(self) -> DeletionResult:
        return self.delete_all(ExampleModel)

    def update_full_example(self, id: int, data: ExampleSchemaCreation) -> ExampleModel:
        return self.basic_update_full_one(ExampleModel, id, data)

    def update_partial_example(self, id: int, data: ExampleSchemaPartialUpdate) -> ExampleModel:
        return self.basic_update_partial_one(ExampleModel, id, data)