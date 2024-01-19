from fastapi import Request, Depends
from utils.endpoint import EndpointInstance
from schemas.base import SuccessResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.auth import TokenSchema, CreateClientSchema, ClientSessionSchema
from services.auth import AuthService, get_current_client
from utils.authorization import allowADFS
from utils.session import createSession

class Auth(EndpointInstance):
    def __init__(self):
        self.path    = "/token-local"
        self.tags    = ['Auth']
        self.methods = {
            'POST' : { 'summary': "Local login", 'description': 'This endpoint is used for local authentication.', 'responses' :{ 200: TokenSchema }}
        }
    
    async def POST(self, request: Request, login: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(createSession)) -> TokenSchema | None:
        return AuthService(session).authenticate(login=login)
    
class AuthADFS(EndpointInstance):
    def __init__(self):
        self.path    = "/token-adfs"
        self.tags    = ['Auth']
        self.methods = {
            'POST' : { 'summary': "ADFS login", 'description': 'This endpoint is used for ADFS authentication.', 'responses' :{ 200: TokenSchema }}
        }
    
    
    async def POST(self, request: Request, login: OAuth2PasswordRequestForm = Depends()) -> TokenSchema | None:
        return AuthADFSService().authenticate(login=login)

class Client(EndpointInstance):
    def __init__(self):
        self.path    = "/client-local"
        self.tags    = ['Auth']
        self.methods = {
            'POST' : { 'summary': "Create user", 'description': 'This endpoint is used for creating a new local user.', 'responses' :{ 200: SuccessResponse }}
        }
    
    async def POST(self, request: Request, client: CreateClientSchema, session: Session = Depends(createSession), auth: ClientSessionSchema = Depends(get_current_client)) -> SuccessResponse:
        return AuthService(session=session, auth=auth, authorization_func=allowADFS).create_client(client=client)