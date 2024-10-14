from fastapi import Request, Depends
from sqlalchemy.orm import Session

from services.auth import get_current_user, validate_roles
from services.status import StatusService
from schemas.base import SuccessResponse
from schemas.auth import UserSessionSchema
from utils.config import config
from utils.endpoint import EndpointInstance
from utils.session import createSession
from utils.depends import get_current_db_settings
from schemas.base import SuccessResponse

class Status(EndpointInstance):
    def __init__(self):
        self.path    = "/status"
        self.tags    = ['Status']
        self.methods = {
            'GET' : { 'summary': "Status endpoint", 'description': 'This endpoint is used to check the status of the app.' }
        }
    
    async def GET(self, request: Request, session: Session = Depends(createSession)):
        #return StatusService(session=session).get_status()
        return SuccessResponse(message="Healthy!", data={"status":"RUNNING"})
    
class StatusDetail(EndpointInstance):
    def __init__(self):
        self.path    = "/status-detail"
        self.tags    = ['Status']
        self.methods = {
            'GET' : { 'summary': "Status detailed endpoint", 'description': 'This endpoint is used to check the detailed status of the app.' }
        }
    
    def GET(self, request: Request, current_db_settings: str = Depends(get_current_db_settings)): 
        return SuccessResponse(message="Healthy!", data={'config.db': config.db, 'current_db_settings': current_db_settings})
