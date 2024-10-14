from fastapi import Request, Depends, Query
from typing import List

from schemas.example import *
from services.example import ExampleService
from utils.endpoint import EndpointInstance
from services.auth import get_current_user, validate_roles
from schemas.auth import UserSessionSchema
from schemas.query_filter import QueryFilterSchema
from sqlalchemy.orm import Session

from utils.session import createSession

class ExampleList(EndpointInstance):
    def __init__(self):
        self.path    = "/examples"
        self.tags    = ["Example"]
        self.methods = {
            'GET' : { 'summary': "Retrieve examples", 'description': 'This endpoint retrieves all the examples with pagination.', 'responses' :{ 200: ExampleSchemaPaginatedResponse }},
            'POST' : { 'summary': "Create example", 'description': 'This endpoint creates an example.', 'responses' :{ 200: ExampleSchemaResponse }},
            'DELETE' : { 'summary': "Delete all examples", 'description': 'This endpoint deletes all example.', 'responses' :{ 200: SuccessResponse }}
        }

    async def GET(self, request: Request, session: Session = Depends(createSession), page: int = Query(1, description="Page number", ge=1), 
                  per_page: int = Query(10, description="Items per page", ge=1), filters=QueryFilterSchema, 
                  auth: UserSessionSchema = Depends(get_current_user)):
        return ExampleService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).get_examples(page=page, per_page=per_page, filters=filters)

    async def POST(self, request: Request, data: ExampleSchemaCreation, session: Session = Depends(createSession), 
                   auth: UserSessionSchema = Depends(get_current_user)):
        return ExampleService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).create_example(data=data)

    async def DELETE(self, request: Request, session: Session = Depends(createSession), 
                     auth: UserSessionSchema = Depends(get_current_user)):
        return ExampleService(session=session, auth=auth, authorization_func=validate_roles, roles=["ADMIN"]).delete_examples()


class Example(EndpointInstance):
    def __init__(self):
        self.path        = "/examples/{example_id}"
        self.tags    = ["Example"]
        self.methods = {
            'GET' : { 'summary': "Get example", 'description': 'This endpoint gets the information for an example.', 'responses' :{ 200: ExampleSchemaResponse }},
            'DELETE' : { 'summary': "Delete example", 'description': 'This endpoint deletes an example.', 'responses' :{ 200: ExampleSchemaResponse }},
            'PUT' : { 'summary': "Update full example", 'description': 'This endpoint updates all attributes on an example.', 'responses' :{ 200: ExampleSchemaResponse }},
            'PATCH' : { 'summary': "Update partial example", 'description': 'This endpoint deletes partial attributres on an example.', 'responses' :{ 200: ExampleSchemaResponse }},
        }
    
    async def GET(self, request: Request, example_id : int, session: Session = Depends(createSession), 
                  auth: UserSessionSchema = Depends(get_current_user)):
        return ExampleService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).get_example(id=example_id)

    async def DELETE(self, request: Request, example_id : int, session: Session = Depends(createSession), 
                     auth: UserSessionSchema = Depends(get_current_user)):
        return ExampleService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).delete_example(id=example_id)

    async def PUT(self, request: Request, example_id : int, data: ExampleSchemaCreation, session: Session = Depends(createSession), 
                  auth: UserSessionSchema = Depends(get_current_user)):
        return ExampleService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).update_full_example(id=example_id, data=data)

    async def PATCH(self, request: Request, example_id : int, data: ExampleSchemaPartialUpdate, session: Session = Depends(createSession), 
                    auth: UserSessionSchema = Depends(get_current_user)):
        return ExampleService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).update_partial_example(id=example_id, data=data)
