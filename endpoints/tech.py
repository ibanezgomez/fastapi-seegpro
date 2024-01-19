from fastapi import Request, Depends, Query
from typing import List

from models.tech import TechModel
from schemas.tech import TechSchemaResponse, TechSchemaPaginatedResponse, TechSchemaPaginated, TechSchemaCreation
from services.tech import TechService
from utils.endpoint import EndpointInstance
from services.auth import get_current_client
from schemas.auth import ClientSessionSchema
from sqlalchemy.orm import Session
from utils.authorization import allowLocal

from utils.session import createSession

class TechList(EndpointInstance):
    def __init__(self):
        self.path    = "/techs"
        self.tags    = ["Tech"]
        self.methods = {
            'GET' : { 'summary': "Retrieve techs", 'description': 'This endpoint retrieves all the techs with pagination.', 'responses' :{ 200: TechSchemaPaginatedResponse }},
            'POST' : { 'summary': "Create tech", 'description': 'This endpoint creates a tech.', 'responses' :{ 200: TechSchemaResponse }}
        }

    async def GET(self, request: Request, session: Session = Depends(createSession), page: int = Query(1, description="Page number", ge=1), per_page: int = Query(10, description="Items per page", ge=1), auth: ClientSessionSchema = Depends(get_current_client)):
        return TechService(session=session, auth=auth, authorization_func=allowLocal).get_techs(page=page, per_page=per_page)

    async def POST(self, request: Request, tech_data: TechSchemaCreation, session: Session = Depends(createSession), auth: ClientSessionSchema = Depends(get_current_client)):
        return TechService(session=session, auth=auth, authorization_func=allowLocal).create_tech(tech_data=tech_data)


class Tech(EndpointInstance):
    def __init__(self):
        self.path        = "/techs/{tech_id}"
        self.tags    = ["Tech"]
        self.methods = {
            'GET' : { 'summary': "Get tech", 'description': 'This endpoint gets the information for a tech.', 'responses' :{ 200: TechSchemaResponse }},
            'DELETE' : { 'summary': "Delete tech", 'description': 'This endpoint deletes a tech.', 'responses' :{ 200: TechSchemaResponse }}
        }
    
    async def GET(self, request: Request, tech_id : str, session: Session = Depends(createSession), auth: ClientSessionSchema = Depends(get_current_client)):
        return TechService(session=session, auth=auth, authorization_func=allowLocal).get_tech(id=tech_id)

    async def DELETE(self, request: Request, tech_id : str, session: Session = Depends(createSession), auth: ClientSessionSchema = Depends(get_current_client)):
        return TechService(session=session, auth=auth, authorization_func=allowLocal).delete_tech(id=tech_id)
