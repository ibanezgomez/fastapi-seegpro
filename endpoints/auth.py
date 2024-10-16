from fastapi import Response, Depends
from utils.endpoint import EndpointInstance
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import TokenSchema, LoginSchema
from services.auth import AuthService
from utils.session import createSession

class Auth(EndpointInstance):
    def __init__(self):
        self.path    = "/login"
        self.tags    = ['Auth']
        self.methods = {
            'POST' : { 'summary': "Local login", 'description': 'This endpoint is used for local authentication.', 'responses' :{ 200: TokenSchema }}
        }
    
    async def POST(self, response: Response, login: LoginSchema, session: Session = Depends(createSession)) -> TokenSchema | None:
        return AuthService(session).authenticate(response=response, login=login)
    
class AuthSwagger(EndpointInstance):
    def __init__(self):
        self.path    = "/login-form"
        self.tags    = ['Auth']
        self.methods = {
            'POST' : { 'summary': "Local login for Swagger", 'description': 'This endpoint is used for local authentication.', 'responses' :{ 200: TokenSchema }}
        }
    
    async def POST(self, response: Response, login: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(createSession)) -> TokenSchema | None:
        login_data: LoginSchema = LoginSchema(username=login.username, password=login.password)
        return AuthService(session).authenticate(response=response, login=login_data)