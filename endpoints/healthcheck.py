from fastapi import Request, Depends
from utils.endpoint import EndpointInstance
from utils.authorization import allowLocal
from services.auth import get_current_client
from services.healthcheck import HealthcheckService
from schemas.base import SuccessResponse
from schemas.auth import ClientSessionSchema

class Healthcheck(EndpointInstance):
    def __init__(self):
        self.path    = "/healthcheck"
        self.tags    = ['Base']
        self.methods = {
            'GET' : { 'summary': "Healthcheck endpoint", 'description': 'This endpoint is used to check if the app is alive.' }
        }
    
    def GET(self, request: Request): 
        return SuccessResponse(message="Healthy!", data=dict(request.headers.raw))

class HealthcheckAuthLocal(EndpointInstance):
    def __init__(self):
        self.path    = "/healthcheck-auth-local"
        self.tags    = ['Base']
        self.methods = {
            'GET' : { 'summary': "Healthcheck endpoint local auth", 'description': 'This endpoint is used to test local auth.' }
        }
    
    def GET(self, request: Request, auth: ClientSessionSchema = Depends(get_current_client)): 
        return HealthcheckService(auth=auth, authorization_func=allowLocal).get_healthcheck(request=request)
