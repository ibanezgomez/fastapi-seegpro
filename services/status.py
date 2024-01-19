from utils.exceptions import CustomException
from services.base import BaseService
from services.setting import SettingService
from schemas.base import SuccessResponse

class StatusService(BaseService):
    @BaseService.HTTPExceptionHandler
    def get_status(self) -> SuccessResponse:
        active = SettingService(self.session).get_setting(id="DB_ACTIVE")
        if active == True:
            return SuccessResponse(message="Healthy!", data={"status":"RUNNING"})
        else:
            raise CustomException(SettingService(self.session).get_setting(id="DB_INACTIVE_MESSAGE"), None, 503)
        return SuccessResponse(message="Healthy!", data={"status":"RUNNING"})
