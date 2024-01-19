from datetime import datetime

class DojoEngagement:
    def get_engagement_by_id(self, id):
        path = "/api/v2/engagements/" + str(id)
        return self.req(mode="GET", path=path)

    def get_first_engagement_by_name_on_product(self, name, product_id):
        path = "/api/v2/engagements/?name=" + name + "&product=" + str(product_id) 
        res = self.req(mode="GET", path=path)

        if res and "results" in res and len(res["results"]) > 0:
            return res["results"][0]
        else:
            return None
        
    def create_engagement(self, product_id, name, description, repo_url="", tracker="", tags=[], commit="", branch=""):
        path = "/api/v2/engagements/"
        now = datetime.now().strftime('%Y-%m-%d')
        data = {
            "name": name, "description": description, "product": product_id, "tags": tags, "status": "Completed", 
            "target_start": now, "target_end": now, "source_code_management_uri": repo_url, "tracker": tracker
        }

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return res["id"]
        else: return None

    def upload_report_to_engagement(self, engagement_id, report_type, report_data, report_file_name, report_tags=[]):
        path = "/api/v2/import-scan/"
        data = {
            "engagement": engagement_id, "scan_type": report_type, "active": True, "verified": False, "tags": report_tags,
            "environment": "Default"
        }

        files = {'file': (report_file_name, report_data)}
        res = self.req(mode='POST', headers={}, path=path, files=files, payload=data)
        
        if res and "test_id" in res: return res["test_id"]
        else: return None