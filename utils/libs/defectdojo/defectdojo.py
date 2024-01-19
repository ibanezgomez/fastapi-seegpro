import requests, enum, re

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

from .services.product import DojoProduct
from .services.product_type import DojoProductType
from .services.engagement import DojoEngagement
from .services.user import DojoUser
from .services.group import DojoGroup
from .services.report import DojoReport

from utils.logger import log

class DefectDojo(DojoProduct, DojoProductType, DojoEngagement, DojoUser, DojoGroup, DojoReport):
    
    def __init__(self, server, username, password, api=True):
        self.server   = server        
        self.username = username        
        self.password = password
        
        if api == True:
            self.token = self.set_token()
        else:
            self.session = self.set_session()

    def req(self, mode, path=None, url=None, auth=True, response_raw=False, headers=None, files=None, payload=None, json=None, skip_resp_code=False, fail_on_req_error=False):
        response=None
        if not url: url=self.server + path
        if headers is None:
            headers = {}
            if mode.upper() in ['GET', 'POST', 'PUT', 'PATCH']:
                if mode.upper() in ['GET']:
                    headers['Accept']='*/*'
                else:
                    headers['Content-Type'] = 'application/json'
        
        if auth: 
            headers["Authorization"] = self.token
        
        try:
            r = requests.request(mode, headers=headers, url=url, json=json, files=files, data=payload, verify=False)
            if r.status_code in [200, 202, 201, 204]:
                if response_raw: response=r.content
                else: response=r.json()
            else:
                #TODO REMOVE LOG HEADERS AND REQ, ONLY FOR TROUBLESHOOT
                # log.error(action="[dojoAPI]", message="Response code (%s) not valid calling Dojo for %s. Response: %s" % (r.status_code, url, r.text))
                log.error(action="[dojoAPI]", message="Response code (%s) not valid calling Dojo for %s. Request: %s. Request headers: %s. Response: %s Response Headers: %s" % (r.status_code, url, json, headers, r.text, r.headers))
                return None
        except Exception as e:
            #TODO REMOVE LOG HEADERS AND REQ, ONLY FOR TROUBLESHOOT
            # log.error(action="[dojoAPI]", message="Unexpected error calling Dojo for %s. Exception: %s" % (url, e))
            log.error(action="[dojoAPI]", message="Unexpected error calling Dojo for %s. Exception: %s. Request: %s. Request headers: %s." % (url, e, json, headers))
            return None
        return response
    
    def set_token(self):
        path = "/api/v2/api-token-auth/"
        data = { 'username': self.username, 'password': self.password }

        result = self.req(mode='POST', path=path, auth=False, json=data)

        if result and 'token': 
            return 'Token '+result['token']
        else: 
            print('Error getting Defect Dojo token')
            return None
        
    def set_session(self):
        session = requests.Session()
        path = "/login?next=/"
        url = self.server + path
    
        response = session.get(url)
        csrf_token_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)

        if csrf_token_match:
            csrf_token = csrf_token_match.group(1)
            data = {'username': self.username, 'password': self.password, "csrfmiddlewaretoken": csrf_token}
            headers = {'Referer': self.server}
            response = session.post(url, data=data, headers=headers)
            return session
        else:
            print('Error getting CSRF Token for Defect Dojo login')
            return None