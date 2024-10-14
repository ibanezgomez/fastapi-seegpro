import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.endpoint import Endpoint, RouterBuilder
from utils.initial_data import initAndPopulate
from utils.config import config
from utils.logger import log
from utils.middlewares import AccessLogMiddleware

from endpoints.healthcheck import Healthcheck, HealthcheckAuthLocal
from endpoints.status import Status, StatusDetail
from endpoints.example import Example, ExampleList
from endpoints.auth import Auth
from endpoints.user import User
from endpoints.notification import Notification

#if __name__ == "__main__":
# Whoami
for l in config.whoami.asText(show_env=True, show_plain_secrets=False).split('\n'):
    log.info(l, action="[main]")

# Init FastAPI
app = FastAPI(title=config.docs_title, docs_url=config.docs_path, openapi_url=config.docs_path+"/openapi.json", swagger_ui_parameters={"defaultModelsExpandDepth": -1}, version=config.version)
    
# Middlewares
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AccessLogMiddleware)

if not initAndPopulate(): 
    exit()

# Endpoints
endpoints = [
    Endpoint(methods=['POST'],                          path="/login",                  instance=Auth()),
    Endpoint(methods=['GET', 'POST', 'DELETE'],         path="/examples",               instance=ExampleList()),
    Endpoint(methods=['GET', 'PUT', 'PATCH', 'DELETE'], path="/examples/{example_id}",  instance=Example()),
    Endpoint(methods=['POST'],                          path="/users",                  instance=User()),
    Endpoint(methods=['GET'],                           path="/healthcheck-auth",       instance=HealthcheckAuthLocal()),
    Endpoint(methods=['GET'],                           path="/healthcheck",            instance=Healthcheck()),
    Endpoint(methods=['GET'],                           path="/status",                 instance=Status()),
    Endpoint(methods=['GET'],                           path="/status-detail",          instance=StatusDetail()),
    Endpoint(methods=['POST'],                          path="/notification",           instance=Notification())
]

# Define & create router
app.include_router(RouterBuilder(prefix=config.base_path, endpoints=endpoints))

# Start FastAPI
#uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
#del uvicorn_log_config["loggers"]
#uvicorn.run(
#    app,
#    host=config.server_host,
#    port=int(config.server_port),
#    log_config=uvicorn_log_config,
#)
