class DojoUser:
    def get_user_by_id(self, id):
        path = "/api/v2/users/" + str(id)
        return self.req(mode="GET", path=path)

    def get_first_user_by_username(self, username):
        path = "/api/v2/users/?username=" + username
        res = self.req(mode="GET", path=path)

        if res and "results" in res and len(res["results"]) > 0:
            return res["results"][0]
        else:
            return None
        
    def create_user(self, username, name, email, is_active=False):
        path = "/api/v2/users/"
        data = {"username": username, "first_name": name, "email": email, "is_active": is_active}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return res["id"]
        else: return None

        #Role 4 is Owner
    def add_product_to_user(self, product_id, user_id, role=4):
        path = "/api/v2/product_members/"
        data = {"product": product_id, "user": user_id, "role":role}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return True
        else: return False

    #Role 4 is Owner
    def add_product_type_to_user(self, product_type_id, user_id, role=4):
        path = "/api/v2/product_type_members/"
        data = {"product_type": product_type_id, "user": user_id, "role":role}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return True
        else: return False