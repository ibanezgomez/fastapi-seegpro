from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.endpoint import Endpoint, RouterBuilder
from utils.initial_data import initAndPopulate
from utils.config import config
from utils.logger import log
from utils.middlewares import AccessLogMiddleware

from endpoints.healthcheck import Healthcheck, HealthcheckAuthLocal
from endpoints.status import Status, StatusDetail
from endpoints.tech import Tech, TechList
from endpoints.auth import Auth, Client
from endpoints.notification import Notification

# Whoami
for l in config.whoami.asText(show_env=True, show_plain_secrets=False).split('\n'):
    log.info(l, action="[main]")

# Init FastAPI
app = FastAPI(title="mepillas", docs_url=config.docs_path, openapi_url=config.docs_path+"/openapi.json", swagger_ui_parameters={"defaultModelsExpandDepth": -1}, version=config.version)
    
# Middlewares
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AccessLogMiddleware)

if not initAndPopulate(): 
    exit()

# Endpoints
endpoints = [
    Endpoint(methods=['GET'],                  path="/healthcheck-auth-local",                     instance=HealthcheckAuthLocal()),
    Endpoint(methods=['GET'],                  path="/healthcheck",                                instance=Healthcheck()),
    Endpoint(methods=['GET'],                  path="/status",                                     instance=Status()),
    Endpoint(methods=['GET'],                  path="/status-detail",                              instance=StatusDetail()),
    Endpoint(methods=['POST'],                 path="/client-local",                               instance=Client()),
    Endpoint(methods=['POST'],                 path="/token-local",                                instance=Auth()),
    Endpoint(methods=['GET', 'POST'],          path="/techs",                                      instance=TechList()),
    Endpoint(methods=['GET', 'DELETE'],        path="/techs/{tech_id}",                            instance=Tech()),
    Endpoint(methods=['POST'],                 path="/notification",                               instance=Notification())
]

# Define & create router
app.include_router(RouterBuilder(prefix=config.base_path, endpoints=endpoints))
