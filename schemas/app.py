import re
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from schemas.base import PaginationResult, SuccessResponse
from schemas.tech import TechSchema
from schemas.profile import ProfileSchema
from utils.config import config

### IN/OUT ###

# Base
class AppSchema(BaseModel): # Base model
    id:            str
    date_created:  datetime
    date_updated:  datetime
    repo_url:      str
    app_name:      str
    owner_id:      str | None
    profile:       ProfileSchema
    tech:          TechSchema | None

class AppSchemaPaginated(PaginationResult): # Base pagination structure
    items: List[AppSchema]

### OUTPUT ###
class AppSchemaResponse(SuccessResponse): # Response one
    data: AppSchema

class AppSchemaListResponse(SuccessResponse): # Response all
    data: List[AppSchema]

class AppSchemaPaginatedResponse(SuccessResponse): # Response pagination
    data: AppSchemaPaginated

### INPUT ###
def obtain_app_id(repo_url):
    return '_'.join(repo_url.split('/')[1:])

def clean_repo_url(repo_url):
    repo_url = re.sub(r'^https://www\.|^http://www\.|^http://|^https://|^www\.', '', repo_url)
    repo_url = re.sub(r'\.git$', '', repo_url)
    return repo_url

class AppSchemaCreation(BaseModel): # Request creation
    repo_url: str
    profile_id: Optional[str]

    @validator("repo_url")
    def validate_repo_url(cls, value):
        repo_url = clean_repo_url(repo_url=value)

        if repo_url.startswith(config.settings.get("DB_GIT_HOST") + "/"):
            return repo_url
        else:
            raise ValueError("The repo_url is not a valid Git repository")