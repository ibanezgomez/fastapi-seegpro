import requests, random, json
import inspect
from utils.logger import log
# from ..logger.logger import logErrorAPI
from requests.packages.urllib3.exceptions import InsecureRequestWarning

baseUrl = 'https://api.telegram.org/bot{}/{}'
gandalfGif = 'https://thumbs.gfycat.com/SlowBronzeDuckbillplatypus-mobile.mp4'
lukeGif = 'https://i0.wp.com/media.giphy.com/media/Xjo8pbrphfVuw/giphy.gif?resize=462%2C260&ssl=1'
sadCatGif = 'https://64.media.tumblr.com/tumblr_m986ntPyfN1qksk74o1_400.gif'
wiggleCatGif = 'https://thumbs.gfycat.com/AlienatedScaredHalibut-small.gif'

class Telegram:
    module = "TELEGRAM"
    token   = None
    chat_id = None

    def __init__(self, token, chat_id):
        self.chat_id=chat_id
        self.token=token
    
    def getChatID(self):
        return self.chat_id

    def setChatID(self, chatid):
        self.chat_id=chatid

    def getAllowedChatIDs(self):
        return [self.getChatID()]
    
    def getToken(self):
        return self.token

    def setToken(self, token):
        self.token=token

    def getMe(self, offset=None):
        try:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            headers = {'Accept': '*/*'}
            url = baseUrl.format(self.getToken(),'getMe')
            response = requests.get(url, headers=headers, verify=False).json()
            if 'ok' in response and response['ok']==True:
                return response['result']
            else:
                return None
        except:
            return None

    def getUpdates(self, offset=None):
        try:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            headers = {'Accept': '*/*'}
            if offset:
                url = baseUrl.format(self.getToken(),'getUpdates?offset='+str(offset))
            else:
                url = baseUrl.format(self.getToken(),'getUpdates')
            response = requests.get(url, headers=headers, verify=False).json()
            if 'ok' in response and response['ok']==True:
                return response['result']
            else:
                return []
        except:
            return []

    def send(self, message, chat_id=None):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        telegram_action = "TELEGRAM"

        if not chat_id: c=self.getChatID()
        else: c=chat_id
        headers = {'Accept': '*/*'}
        data = {
            'chat_id': c,
            'text': message,
            'disable_notification': False,
            'parse_mode': 'HTML'
        }
        try:
            url = baseUrl.format(self.getToken(), 'sendMessage')
            response = requests.post(url, data=data, headers=headers, verify=False)
        except Exception as e:
            log.error(action=telegram_action, message=f"Error while sending a message. Exception: {e}")

        if response.status_code == 200:
            log.info(action=telegram_action, message="Notification sended OK")
            return True
        else:
            log.error(action=telegram_action, message="Failed to send notification")
            return False

    def sendMessage(self, chatId, message, disableNotification, encoding):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        headers = {'Accept': '*/*'}
        data = {
            'chat_id': chatId,
            'text': message,
            'disable_notification': disableNotification,
            'parse_mode': encoding
        }

        url = baseUrl.format(self.getToken(), 'sendMessage')
        response = requests.post(url, data=data, headers=headers, verify=False)

    def sendImg(self, img_path, chatId):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        img=open(img_path, 'rb')
        multipart_form_data = {
            'photo': img
        }
        data = {
            'chat_id': chatId
        }
        url = baseUrl.format(self.getToken(), 'sendPhoto')
        response = requests.post(url, data=data, files=multipart_form_data, verify=False)

    def sendImage(self, img_path):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        img=open(img_path, 'rb')
        multipart_form_data = {
            'photo': img
        }
        data = {
            'chat_id': self.getChatID()
        }
        url = baseUrl.format(self.getToken(), 'sendPhoto')
        response = requests.post(url, data=data, files=multipart_form_data, verify=False)
    
    def sendVideo(self, video_path):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        video=open(video_path, 'rb')
        multipart_form_data = {
            'video': video
        }
        data = {
            'chat_id': self.getChatID()
        }
        url = baseUrl.format(self.getToken(), 'sendVideo')
        response = requests.post(url, data=data, files=multipart_form_data, verify=False)

    def sendAnimation(self, chatId, animation, disableNotification):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        headers = {'Accept': '*/*'}
        data = {
            'chat_id': chatId,
            'animation': animation,
            'disable_notification': disableNotification
        }

        url = baseUrl.format(self.getToken(), 'sendAnimation')
       

        response = requests.post(url, data=data, headers=headers, verify=False)
    
    def sendAnimation(self, chatId, animation, disableNotification):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        headers = {'Accept': 'application/json'}
        data = {
            'chat_id': chatId,
            'animation': animation,
            'disable_notification': disableNotification
        }

        url = baseUrl.format(self.getToken(), 'sendAnimation')

    def sendButtons(self, chatId, buttons=None): # butons = {'reply_markup' : {'inline_keyboard': [[{'text': 'Opcion 1', 'callback_data': 'opc1_cmd'},{'text': 'Opcion 2', 'callback_data': 'opc2_cmd'}]] }, 'text': 'Elige una de las siguientes optiones:'}
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        headers = {'Accept': '*/*'}
        text='Elige una de las siguientes optiones:'
        reply_markup={'inline_keyboard': [[{'text': 'Opcion 1', 'callback_data': 'opc1_cmd'},{'text': 'Opcion 2', 'callback_data': 'opc2_cmd'}]] }
        
        if buttons and 'text' in buttons:
            text=buttons['text']
        if buttons and 'reply_markup' in buttons:
            reply_markup=buttons['reply_markup']    
        
        data = {'chat_id': chatId, 'text': text, 'reply_markup': json.dumps(reply_markup)}

        url = baseUrl.format(self.getToken(), 'sendMessage')
        response = requests.post(url, headers=headers, data=data, verify=False)


    def criticalGradeMessage(self, chatId, mark):
        gifNumber = random.randint(1, 3)
        message = '<b>Critical</b>\nApp: {}\nEngine: {}\nThe grade of this app has worsened\nPrevious grade: {}\nNew grade: {}'.format(mark['app'], mark['engine'],
mark['previous_grade'], mark['grade'])
        self.sendMessage(chatId, message, False, 'HTML')
        if gifNumber <= 1:
            self.sendAnimation(chatId, lukeGif, True)
        else:
            self.sendAnimation(chatId, sadCatGif, True)

    def successfulGradeMessage(self, chatId, mark):
        gifNumber = random.randint(1, 3)
        message = '<b>Success</b>\nApp: {}\nEngine: {}\nGrade: 10\n'.format(mark['app'], mark['engine'])
        self.sendMessage(chatId, message, True, 'HTML')
        if gifNumber <= 1:
            self.sendAnimation(chatId, wiggleCatGif, True)
        else:
            self.sendAnimation(chatId, gandalfGif, True)

