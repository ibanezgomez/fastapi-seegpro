from pydantic import Field
from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse
from schemas.base import *

# Evita duplicar código en diferentes endpoints y trae funciones por defecto
class EndpointInstance:
    def getDefaultMethodsMetadata(self):
        return {
            'GET'    : { 'summary': "GET default summary",    'description': "Undefined GET description"},
            'POST'   : { 'summary': "POST default summary",   'description': "Undefined POST description"},
            'PUT'    : { 'summary': "PUT default summary",    'description': "Undefined PUT description"},
            'DELETE' : { 'summary': "DELETE default summary", 'description': "Undefined DELETE description"}
        }
    
    def getDefaultResponses(self):
        return {
            200: {'model': SuccessResponse},
            400: {'model': BadRequestResponse},
            401: {'model': UnauthorizedResponse},
            403: {'model': ForbiddenResponse},
            404: {'model': NotFoundResponse}, 
            409: {'model': IntegrityErrorResponse}, 
            500: {'model': ServerErrorResponse},
            503: {'model': ServiceUnavailableResponse}
        }

    def GET(self, request: Request):    return self.defaultResponse(request, "method GET not implemented")
    def POST(self, request: Request):   return self.defaultResponse(request, "method POST not implemented")
    def PUT(self, request: Request):    return self.defaultResponse(request, "method PUT not implemented")
    def DELETE(self, request: Request): return self.defaultResponse(request, "method DELETE not implemented")
    def defaultResponse(self, request: Request, message: str):
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
        }
        if request.method == 'POST' and 'body' in request: 
            request_data["body"]=dict(request.body())
        return JSONResponse(status_code=200, content={"success":True, "message": message, "request": request_data}) 

# Clase que adapta al router de fast api
class Endpoint:
    def __init__(self, instance: object, path: str='',  methods: list=None):
        self.instance=instance
        # Methods Stage:
        # Methods: 1º Defined by __init__ methods arg, 2º Defined in instance file
        if methods != None: 
            self.methods = {method: {} for method in methods}
        else: 
            if isinstance(self.instance.methods, dict) and self.instance.methods.keys()>0:
                self.methods = self.instance.methods
            elif isinstance(self.instance.methods, list) and len(self.instance.methods)>0:
                self.methods = {method: {} for method in self.instance.methods}
            else:
                self.methods = {method: {} for method in methods}

        methods_default_metadata=self.instance.getDefaultMethodsMetadata()
        for m in self.methods.keys():
            if m not in methods_default_metadata.keys():
                print("Error, invalid method: %s" % (m))
                exit()

        # Summary & description Stage:
        # From endpoint Instance
        for m in self.methods.keys():
            if hasattr(self.instance, 'methods') and isinstance(self.instance.methods, dict) and m in self.instance.methods and 'summary' in self.instance.methods[m]: self.methods[m]['summary']=self.instance.methods[m]['summary']
            else: self.methods[m]['summary']=methods_default_metadata[m]['summary']
            if hasattr(self.instance, 'methods') and isinstance(self.instance.methods, dict) and m in self.instance.methods and 'description' in self.instance.methods[m]: self.methods[m]['description']=self.instance.methods[m]['description'] 
            else: self.methods[m]['description']=methods_default_metadata[m]['description']

        # Path: 1º Defined by __init__ path arg, 2º Defined in instance file. Always update the instance with the final path.
        if path != '': 
            if hasattr(instance, 'path') and str(instance.path) != path:
                print("Endpoint path declared != Instance path, will be set to: %s" % (path))
            self.path=path
        else: 
            if hasattr(instance, 'path') and str(instance.path) != '':
                self.path=instance.path
            else:
                print("Error, path not declared")
                exit()

        self.responses     = self.instance.getDefaultResponses()
        #print("Generated endpoint: %s, methods:%s responses: %s" % (self.path, self.methods,  self.responses ))
    
    def getHandler(self, method: str):
        if hasattr(self.instance, method) and callable(getattr(self.instance, method)): return getattr(self.instance, method)
        else: return self.unknownHandler
    def getSummary(self, method: str): return self.methods[method]['summary']
    def getDescription(self, method: str): return self.methods[method]['description']
    def getMethods(self): return self.methods
    def getPath(self): return self.path
    def getTags(self): 
        if hasattr(self.instance, 'tags'): return self.instance.tags
        return []
    def getResponses(self, method: str): 
        detail_responses=self.responses
        if hasattr(self.instance, 'methods') and isinstance(self.instance.methods, dict) and method in self.instance.methods.keys() and 'responses' in self.instance.methods[method]: 
            for r in self.instance.methods[method]['responses'].keys():
                detail_responses[r]={'model': self.instance.methods[method]['responses'][r]}
        return detail_responses
    
    def unknownHandler(self, request: Request):
        return self.instance.defaultResponse(request, "The instance not has the resource")
    
def RouterBuilder(prefix: str, endpoints: List[Endpoint]):
    router = APIRouter(prefix=prefix)
    for e in endpoints:
        for m in e.getMethods():
            router.add_api_route(path=e.getPath(), endpoint=e.getHandler(m), methods=[m], responses=e.getResponses(m), summary=e.getSummary(m), description=e.getDescription(m), tags=e.getTags())
    return router
