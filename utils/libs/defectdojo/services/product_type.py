class DojoProductType:
    def get_product_type_by_id(self, id):
        path = "/api/v2/product_types/" + str(id)
        return self.req(mode="GET", path=path)

    def get_first_product_type_by_name(self, name):
        path = "/api/v2/product_types/?name=" + name
        res = self.req(mode="GET", path=path)

        if res and "results" in res and len(res["results"]) > 0:
            return res["results"][0]
        else:
            return None
        
    def create_product_type(self, name, description=""):
        path = "/api/v2/product_types/"
        data = {"name": name, "description": description}

        res = self.req(mode='POST', path=path, json=data)
        
        if res and "id" in res: return res["id"]
        else: return None