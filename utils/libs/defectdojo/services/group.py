class DojoGroup:
    def get_group_by_id(self, id):
        path = "/api/v2/dojo_groups/" + str(id)
        return self.req(mode="GET", path=path)

    def get_first_group_by_name(self, name):
        path = "/api/v2/dojo_groups/?name=" + name
        res = self.req(mode="GET", path=path)

        if res and "results" in res and len(res["results"]) > 0:
            return res["results"][0]
        else:
            return None
        
    def create_group(self, name, description=""):
        path = "/api/v2/dojo_groups/"
        data = {"name": name, "description": description}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return res["id"]
        else: return None

    #Role 4 is Owner
    def add_user_to_group(self, user_id, group_id, role=4):
        path = "/api/v2/dojo_group_members/"
        data = {"user": user_id, "group": group_id, "role":role}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return True
        else: return False

    #Role 4 is Owner
    def add_product_to_group(self, product_id, group_id, role=4):
        path = "/api/v2/product_groups/"
        data = {"product": product_id, "group": group_id, "role":role}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return True
        else: return False

    #Role 4 is Owner
    def add_product_type_to_group(self, product_type_id, group_id, role=4):
        path = "/api/v2/product_type_groups/"
        data = {"product_type": product_type_id, "group": group_id, "role":role}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return True
        else: return False