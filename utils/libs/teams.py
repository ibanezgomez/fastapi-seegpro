import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import inspect
from utils.logger import log
# from ..logger.logger import logErrorAPI

class Teams:
    module = "TEAMS"
    webhook = None

    def __init__(self, webhook):
        self.webhook = webhook

    def getWebhook(self): return self.webhook
    def setWebhook(self, webhook): self.webhook=webhook

    def sendMessage(self, title, text, themeColor="d63333"):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        data = {
            'title': title,
            'themeColor' : themeColor,
            'text': text
        }

        response = requests.post(self.webhook, json=data, verify=False)

        if response.status_code == 200:
            return True
        else:
            log.error(action="TEAMS", message="Failed to send notification")
            
            return False
        # else:
        #     logErrorAPI(module=self.module, func=inspect.stack()[0].function, path="/IncomingWebhook", method="POST", response=response, data=data)
        #     return False