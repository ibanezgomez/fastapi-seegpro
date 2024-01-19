from services.notification import  NotificationServiceLocal
from utils.enums import NotificationLevel
from schemas.notification import NotificationSchemaCreation

class NotificationEvents():
    EVENTS = ["PipelineBlocked"]

    def __init__(self):
        self.notification_service = NotificationServiceLocal()

    def notify(self, message, level):
        self.notification_service.create_notification(NotificationSchemaCreation(message=message, level=level))

    #PipelineBlocked
    def pipeline_blocked_event(self, scan_id, app_id, detail_message):
        try:
            engines_fail = detail_message.split("\n")
            custom_detail_message = []
            for e in engines_fail:
                if "Engine" in e:
                    eng = e.split(" ")[1]
                    sev = e.split(" ")[6].split("_")[0][0].upper()
                    thresh = e.split(" ")[7].replace("(","").replace(")","").replace(",","")
                    link = e.split(" ")[11][:-1]
                    link_data = '<a href="' + link + '">🔗</a>'
                    custom_detail_message.append(f"- <u>{eng}</u> {sev} thresh. exceeded ({thresh}) {link_data}")
            
            message = f"<b>PIPELINE BLOQUEADA</b>\n\n<b>APP:</b> {app_id}\n<b>SCAN ID:</b> {scan_id}\n<b>DETAILS:</b>\n"+'\n'.join(custom_detail_message)
            self.notify(message=message, level=NotificationLevel.CRITICAL)
        except: pass

    def pipeline_error_event(self, scan_id, app_id):
        try:
            message = f"<b>ERROR 409</b>\n\n<b>APP:</b> {app_id}\n<b>SCAN ID:</b> {scan_id}\n<b>DETAILS:</b> Posible Pipeline Parada."
            self.notify(message=message, level=NotificationLevel.CRITICAL)
        except: pass