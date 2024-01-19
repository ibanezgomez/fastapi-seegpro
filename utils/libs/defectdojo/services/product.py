class DojoProduct:
    def get_product_by_id(self, id):
        path = "/api/v2/products/" + str(id)
        return self.req(mode="GET", path=path)

    def get_first_product_by_name(self, name):
        path = "/api/v2/products/?name_exact=" + name
        res = self.req(mode="GET", path=path)

        if res and "results" in res and len(res["results"]) > 0:
            return res["results"][0]
        else:
            return None
        
    def create_product(self, name, description, prod_type_id=None, tags=[], external=False, user_id=None):
        path = "/api/v2/products/"
        data = {"tags": tags, "name": name, "description": description, "internet_accessible": external, "prod_type": prod_type_id, "team_manager" : user_id}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return res["id"]
        else: return None