from fastapi import Request, Depends, Query
from sqlalchemy.orm import Session

from schemas.auth import ClientSessionSchema
from schemas.notification import NotificationSchemaCreation
from schemas.base import SuccessResponse

from services.auth import get_current_client
from services.notification import NotificationService

from utils.endpoint import EndpointInstance
from utils.authorization import allowLocal
from utils.session import createSession
from utils.queues import queue_manager

class Notification(EndpointInstance):
    def __init__(self):
        self.path    = "/notification"
        self.tags    = ["Notification"]
        self.methods = {
            'POST' : { 'summary': "Create notification", 'description': 'This endpoint creates a notification.', 'responses' :{ 200: SuccessResponse }}
        }

    async def POST(self, request: Request, notification_data: NotificationSchemaCreation, session: Session = Depends(createSession), auth: ClientSessionSchema = Depends(get_current_client)):
        return NotificationService(session=session, auth=auth, authorization_func=allowLocal).create_notification(notification_data=notification_data)
