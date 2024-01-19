import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from utils.logger import log

MAINTAINER_ROL_NAME = "MAINTAINER"

class Gitlab:
    host = None
    access_token = None

    api_path = "/api/graphql"

    def __init__(self, host, access_token):
        self.host = host
        self.access_token = access_token

    def req(self, data):
        headers = {"Authorization": "Bearer " + self.access_token}
        url="https://" + self.host + self.api_path

        try:
            result = requests.post(url=url, json=data, headers=headers)
            return result
        except Exception as e:
            log.error(action="[gitAPI]", message="Unexpected error calling Gitlab for %s. Exception: %s" % (url, e))
            return None
    
    #Graphql to obtain most used language
    def get_project_most_used_language(self, repo_full_path):
        query = """
            query
            {
                project(fullPath: "<REPO_FULL_PATH>")
                {
                    languages{
                        name
                        share
                    }
                }
            }
        """
        data = {'query': query.replace("<REPO_FULL_PATH>", repo_full_path)}
        response = self.req(data=data)
        language = None

        if response and response.status_code == 200 and "data" in response.json() and "project" in response.json()["data"] and response.json()["data"]["project"] != None:
            graphql_project_data = response.json()['data']['project']
            
            if "languages" in graphql_project_data and graphql_project_data["languages"]: 
                language = max(graphql_project_data["languages"], key=lambda lang: lang["share"])["name"]

        return language

    #Graphql to obtain maintainers
    def get_project_maintainers(self, repo_full_path):
        query = """
            query
            {
                project(fullPath: "<REPO_FULL_PATH>")
                {
                    projectMembers {
                        nodes{
                            user{
                                username
                            }
                            accessLevel {
                                stringValue
                            }
                        }
                    }
                }
            }
        """
        data = {'query': query.replace("<REPO_FULL_PATH>", repo_full_path)}
        response = self.req(data=data)
        maintainers = []

        if response and response.status_code == 200 and "data" in response.json() and "project" in response.json()["data"] and response.json()["data"]["project"] != None:
            graphql_project_data = response.json()['data']['project']
            
            if "projectMembers" in graphql_project_data and graphql_project_data["projectMembers"]:
                project_members_data = graphql_project_data["projectMembers"]
                if "nodes" in project_members_data and project_members_data["nodes"]:
                    members = project_members_data["nodes"]
                    for member in members:
                        if member['accessLevel']['stringValue'] == MAINTAINER_ROL_NAME and member["user"]["username"] not in maintainers:
                            maintainers.append(member["user"]["username"])

        return maintainers
