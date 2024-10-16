from fastapi import Request, Depends, Response
from utils.endpoint import EndpointInstance
from sqlalchemy.orm import Session
from schemas.biometric import *
from schemas.auth import UserSessionSchema, TokenSchema
from schemas.base import SuccessResponse
from services.auth import get_current_user, validate_roles
from services.biometric import BiometricService
from utils.session import createSession

class BiometricChallenge(EndpointInstance):
    def __init__(self):
        self.path    = "/biometric/challenge"
        self.tags    = ['Biometric']
        self.methods = {
            'GET' : { 'summary': "Get FIDO challenge for biometric register", 'description': 'This endpoint is used for generating FIDO challenge for biometric register', 'responses' :{ 200: BiometricChallengeSchemaResponse }}
        }
    
    async def GET(self, response: Response, session: Session = Depends(createSession),
                  auth: UserSessionSchema = Depends(get_current_user)) -> BiometricChallengeSchemaResponse | None:
        return BiometricService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).get_biometric_challenge()

class BiometricRegister(EndpointInstance):
    def __init__(self):
        self.path    = "/biometric/register"
        self.tags    = ['Biometric']
        self.methods = {
            'POST' : { 'summary': "Save biometric for user", 'description': 'This endpoint is used for saving biometric for user.', 'responses' :{ 200: SuccessResponse }}
        }
    
    async def POST(self, request: Request, biometric_data: BiometricRegisterSchema, session: Session = Depends(createSession), 
                   auth: UserSessionSchema = Depends(get_current_user)) -> SuccessResponse:
        return BiometricService(session=session, auth=auth, authorization_func=validate_roles, roles=["USER"]).register_biometric(biometric_data=biometric_data)
    
class BiometricLogin(EndpointInstance):
    def __init__(self):
        self.path    = "/biometric/login"
        self.tags    = ['Biometric']
        self.methods = {
            'POST' : { 'summary': "Local login with biometric", 'description': 'This endpoint is used for local authentication with biometric.', 'responses' :{ 200: TokenSchema }}
        }
    
    async def POST(self, response: Response, login: BiometricLoginSchema, session: Session = Depends(createSession)) -> TokenSchema | None:
        return BiometricService(session).login_biometric(response=response, login=login)