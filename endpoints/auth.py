from fastapi import Response, Depends
from utils.endpoint import EndpointInstance
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
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
    
    async def POST(self, response: Response, login: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(createSession)) -> TokenSchema | None:
        token_schema: TokenSchema = AuthService(session).authenticate(login=login)

        #Add as header also for FWK Front
        response.headers["Authorization"] = token_schema.access_token
        
        return token_schema