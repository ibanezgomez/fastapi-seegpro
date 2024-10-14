from fastapi import Request, Depends
from utils.endpoint import EndpointInstance
from schemas.base import SuccessResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.auth import TokenSchema
from services.auth import AuthService
from utils.session import createSession

class Auth(EndpointInstance):
    def __init__(self):
        self.path    = "/login"
        self.tags    = ['Auth']
        self.methods = {
            'POST' : { 'summary': "Local login", 'description': 'This endpoint is used for local authentication.', 'responses' :{ 200: TokenSchema }}
        }
    
    async def POST(self, request: Request, login: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(createSession)) -> TokenSchema | None:
        return AuthService(session).authenticate(login=login)