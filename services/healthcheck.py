from schemas.base import SuccessResponse
from services.base import BaseDataManager, BaseService
from fastapi import Request

class HealthcheckService(BaseService):
    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def get_healthcheck(self, request: Request) -> SuccessResponse:
        return SuccessResponse(message="Healthy!", data={'headers': dict(request.headers.raw), 'client': self.auth.client.dict()})

class HealthcheckDataManager(BaseDataManager):
    pass
     
