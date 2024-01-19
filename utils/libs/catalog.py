import urllib3
urllib3.disable_warnings()
import enum
import requests
import re
from utils.logger import log

ID_ROLES = [581, 563, 562, 584]
ID_ALIAS = 227
ID_DESC = 721
ROLES = ["RT", "RF", "R"]
CLEANR = re.compile('<.*?>')

class ContactRole(enum.Enum):
    RT = 'RT' 
    RF = 'RF'
    R  = 'R'

class Catalog:
    host = None
    token = None
    api_path = "/rest/insight/1.0"

    def __init__(self, host, token):
        self.host = host
        self.token = token

    def req(self, method, path, data=None, headers=None):
        if not headers:
            headers = {}

        headers["Authorization"] = "Bearer " + self.token

        url = "https://" + self.host + self.api_path + path

        try:
            if method.upper() == 'GET':
                result=requests.get(url = url, verify=False, headers=headers)
            elif method.upper() == 'POST':
                result=requests.post(url = url, verify=False, json = data, headers=headers)
            elif method.upper() == 'DELETE':
                result=requests.delete(url = url, verify=False, headers=headers)
            elif method.upper() == 'PATCH':
                result=requests.patch(url = url, verify=False, json = data, headers=headers)
            elif method.upper() == 'PUT':
                result=requests.put(url = url, verify=False, json = data, headers=headers)
            return result
        except Exception as e:
            log.error(action="[jiraAPI]", message="Unexpected error calling Jira Catalog for %s. Exception: %s" % (url, e))
            return None
    
    def search_owner(self, app_name):
        try: 
            res = self.get_responsable(app_name)
            if res != None:
                for app in res['data']:
                    #Si el grupo coincide exactamente con el nombre de la app encontrada
                    if app_name.upper() == app["portal_name"].upper() or app_name.upper() == app["alias"].upper():
                        owner_found = None

                        for owner in app["owners"]:
                            #Si no existe owner aún, pone el actual y si es RT, deja de buscar
                            if not owner_found:
                                owner_found = owner["username"]
                                if ContactRole.RT in owner["roles"]: break

                            #Si ya existe y sigue ejecutando, significa que aún no es RT
                            else:
                                #Si el nuevo owner es RT, lo pone a él y deja de buscar
                                if ContactRole.RT in owner["roles"]:
                                    owner_found = owner["username"]
                                    break
                        
                        #Si ha encontrado owner, lo pone como contacto
                        if owner_found: return owner_found
        except: 
            pass

        return None
    
    def get_responsable(self, input):
        path = F'/aql/objects?qlQuery=("Nombre" like "' + input + '" or "Abreviatura" like "' + input + '" or "Responsable" like "' + input + '" or "Responsable Técnico" like "' + input + '" or "Responsable Funcional" like "' + input + '") and objectSchemaId=21&includeTypeAttributes=False&includeExtendedInfo=False&resultPerPage=200'

        response = self.req("GET", path)
        if response and response.status_code == 200:
            if response.json()["objectEntries"] and len(response.json()["objectEntries"]) != 0:
                results = {}
                results["data"] = []

                for entry in response.json()["objectEntries"]:
                    portal_dict = {}
                    portal_dict["search_param"] = input
                    portal_dict["portal_name"] = entry["label"]
                    portal_dict["alias"] = ""
                    portal_dict["owners"] = []

                    for attr in entry["attributes"]:
                        if attr["objectTypeAttributeId"] in ID_ROLES:
                            for object in attr["objectAttributeValues"]:
                                friendly_name = object["displayValue"].split("(")[0][:-1]
                                username = object["displayValue"].split("(")[1].replace(")", "")

                                add = True
                                for owner in portal_dict["owners"]:
                                    if username == owner.get("username"):
                                        add = False

                                if add:
                                    owner_dict = {}
                                    owner_dict["friendly_name"] = friendly_name
                                    owner_dict["username"] = username
                                    owner_dict["roles"] = []

                                    portal_dict["owners"].append(owner_dict)

                                if attr["objectTypeAttributeId"] == 581 or attr["objectTypeAttributeId"] == 584:
                                    owner_dict["roles"].append(ROLES[2])
                                elif attr["objectTypeAttributeId"] ==  563:
                                    owner_dict["roles"].append(ROLES[0])
                                elif attr["objectTypeAttributeId"] ==  562:
                                    owner_dict["roles"].append(ROLES[1])
                        
                        elif attr["objectTypeAttributeId"] == ID_ALIAS:
                            portal_dict["alias"] = attr["objectAttributeValues"][0]["displayValue"]

                        elif attr["objectTypeAttributeId"] == ID_DESC:
                            portal_dict["description"] = re.sub(CLEANR, '', attr["objectAttributeValues"][0]["displayValue"])

                    results["data"].append(portal_dict)

                results["total"] = response.json()["totalFilterCount"]
                results["totalPage"] = response.json()["toIndex"]
                return results
            else:
                return None
        else:
            return None

    def get_user_data(self, input):
        path = f'/aql/objects?qlQuery=(Name like "{input}" or Teléfonos like "{input}") and objectTypeId = 82&includeTypeAttributes=False&includeExtendedInfo=False&resultPerPage=200'
        response = self.req("GET", path)

        if response and response.status_code == 200 and len(response.json().get("objectEntries")) != 0:
            results = {}
            results["data"] = {}

            for entry in response.json()["objectEntries"]:
                phone = ''
                email = ''
                puesto = ''
                div = ''
                dpto = ''
                for attr in entry["attributes"]:
                    if attr["objectTypeAttributeId"] == 416:
                        user = attr["objectAttributeValues"][0]["value"]
                    if attr["objectTypeAttributeId"] ==  701:
                        phone = attr["objectAttributeValues"][0]["value"]
                        phone = f'({phone.replace("0034 ", "").replace("0035 ", "")})' if phone else None
                        phone = re.findall(r'(\d{9})', phone) if phone else None
                        phone = phone[0] if phone and len(phone) > 0 else None
                    elif attr["objectTypeAttributeId"] ==  417:
                        email = attr["objectAttributeValues"][0]["value"]
                    elif attr["objectTypeAttributeId"] ==  1289:
                        puesto = attr["objectAttributeValues"][0]["displayValue"]
                    elif attr["objectTypeAttributeId"] ==  419:
                        div = attr["objectAttributeValues"][0]["displayValue"]
                    elif attr["objectTypeAttributeId"] ==  1288:
                        dpto = attr["objectAttributeValues"][0]["displayValue"]

                results["data"][user] = {}
                
                results["data"][user]["id"] = input
                results["data"][user]["name"] = re.sub(r'\s*\([^)]*\)\s*', '', entry["label"])
                results["data"][user]["email"] = email
                results["data"][user]["phone"] = phone
                results["data"][user]["position"] = puesto
                results["data"][user]["area"] = div
                results["data"][user]["department"] = dpto

            results["total"] = response.json()["totalFilterCount"]
            results["totalPage"] = response.json()["toIndex"]

            if input in results["data"] and "email" in results["data"][input] and "id" in results["data"][input]:
                return results["data"][input]
            else:
                return None
        return None
