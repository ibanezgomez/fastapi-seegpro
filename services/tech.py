from sqlalchemy import select
from models.tech import TechModel
from schemas.base import PaginationResult
from schemas.tech import TechSchema, TechSchemaResponse, TechSchemaPaginatedResponse, TechSchemaCreation
from services.base import BaseDataManager, BaseService
from datetime import datetime
from utils.logger import log
from utils.libs.gitlab import Gitlab
from utils.config import config

class TechService(BaseService):

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def get_tech(self, id: str) -> TechSchemaResponse:
        """Get tech by ID."""
        # return TechDataManager(self.session).get_tech(id=id).to_schema_response(TechSchemaResponse)
        return TechDataManager(self.session).get_tech(id=id).to_schema_response(TechSchemaResponse)

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def get_techs(self, page: int, per_page: int)-> TechSchemaPaginatedResponse:
        """Get techs paginated."""
        result = TechDataManager(self.session).get_techs(page, per_page)
        result.items=self.getSchemasFromModels(result.items,TechSchema)
        return TechSchemaPaginatedResponse(data=result)

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def create_tech(self, tech_data: TechSchemaCreation) -> TechSchemaResponse:
        """Create a tech."""
        return TechDataManager(self.session).create_tech(tech_data).to_schema_response(TechSchemaResponse)
    
    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def delete_tech(self, id: str) -> TechSchemaResponse:
        return TechDataManager(self.session).delete_tech(id).to_schema_response(TechSchemaResponse)

class TechDataManager(BaseDataManager):
   
    def get_default_tech_for_group(self, group: str) -> TechModel:
        stmt = select(TechModel).filter_by(group=group, default=True).order_by(TechModel.date_created)
        tech = self.get_one(stmt)
        return tech

    def get_tech(self, **kwargs) -> TechModel:
        stmt = select(TechModel).filter_by(**kwargs)
        model = self.get_one(stmt)
        return model

    def get_techs(self, page: int, per_page: int) -> PaginationResult:       
        return self.get_paginated(TechModel, page=page, per_page=per_page)

    def create_tech(self, tech_data: TechSchemaCreation) -> TechModel:
        tech_data_dict = tech_data.dict()
        tech_data_dict['date_created'] = datetime.utcnow()
        model = TechModel(**tech_data_dict)
        self.add_one(model)
        return model

    def delete_tech(self, id: str) -> TechModel:
        stmt = select(TechModel).where(TechModel.id == id)
        model = self.get_one(stmt)
        if model.id:
            self.delete_one(model)
        return model