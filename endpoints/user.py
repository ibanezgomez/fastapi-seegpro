from fastapi import Request, Depends
from utils.endpoint import EndpointInstance
from sqlalchemy.orm import Session
from schemas.user import CreateUserSchema, UserSchemaResponse
from schemas.auth import UserSessionSchema
from services.auth import get_current_user, validate_roles
from services.user import UserService
from utils.session import createSession

class User(EndpointInstance):
    def __init__(self):
        self.path    = "/users"
        self.tags    = ['User']
        self.methods = {
            'POST' : { 'summary': "Create user", 'description': 'This endpoint is used for creating a new local user.', 'responses' :{ 200: UserSchemaResponse }}
        }
    
    async def POST(self, request: Request, user: CreateUserSchema, session: Session = Depends(createSession), 
                   auth: UserSessionSchema = Depends(get_current_user)) -> UserSchemaResponse:
        return UserService(session=session, auth=auth, authorization_func=validate_roles, roles=["ADMIN"]).create_user(user=user)