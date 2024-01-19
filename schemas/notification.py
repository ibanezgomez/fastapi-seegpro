from pydantic import BaseModel
from utils.enums import NotificationLevel

### INPUT ###
class NotificationSchemaCreation(BaseModel): # Request creation
    message: str
    level: NotificationLevel
