from schemas.base import SuccessResponse

from services.base import BaseService
from utils.libs.daemon import Daemon

from schemas.notification import NotificationSchemaCreation

from utils.config import config
from utils.logger import log
from utils.libs.telegram import Telegram

class NotificationService(BaseService):

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def create_notification(self, notification_data: NotificationSchemaCreation) -> SuccessResponse:
        """Create notification"""
        return NotificationServiceLocal().create_notification(notification_data)
   
class  NotificationServiceLocal():
    def create_notification(self, notification_data: NotificationSchemaCreation) -> SuccessResponse | None:

        message = notification_data.message
        level   = notification_data.level.value

        if not config.db.get("DB_TELEGRAM_ENABLED", False):
            log.error(action="[NOTIFICATION]", message=f"Telegram is not enabled. Could not notify to {level} group: {message}")
            return SuccessResponse(message="OK", data={"status":"Telegram notification disabled"})
        
        token   = config.secrets.telegram_token
        chat_id = config.db.get(f"DB_TELEGRAM_CHATID_{level}")

        Daemon(func=Telegram(chat_id=chat_id, token=token).send, args=message).start()

        log.info(action="[NOTIFICATION]", message=f"Notified to {level} group: {message}")
        return SuccessResponse(message="OK", data={"status":"Notification sended"})
