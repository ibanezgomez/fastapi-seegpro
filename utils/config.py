from pydantic import BaseModel
from pydantic_settings import (BaseSettings, SettingsConfigDict)
from utils.libs.whoami import Whoami
from typing import List
#from services.setting import SettingServiceLocal

class Secrets(BaseSettings):
    """Secrets configuration parameters.

    Automatically read modifications to the configuration secrets
    from environment variables and ``.env`` file.

    Priority: 1º enviroment variables, 2º .env file
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="APP_SECRET_", case_sensitive=False)
    db_url: str
    shared_seed: str
    def_client_id: str
    def_client_secret: str

class Config(BaseSettings):
    """App settings parameters.

    Automatically read modifications to the configuration parameters
    from environment variables and ``.env`` file.

    Priority: 1º enviroment variables, 2º .env file
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="APP_", case_sensitive=False)
    name:          str
    env:           str
    port:          str
    version:       str
    base_path:     str
    docs_path:     str
    secrets:       Secrets = Secrets()
    whoami:        Whoami = Whoami()
    db:            dict = {}

    def set_db_settings(self):
        from services.setting import SettingServiceLocal
        self.db = SettingServiceLocal().get_settings()
        return self.db

config = Config()
#config.set_db_settings()
