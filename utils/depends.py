from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from services.setting import SettingServiceLocal

# Dependencia común
def get_current_db_settings():
    #return config.set_db_settings()
    return SettingServiceLocal().get_settings()

# Dependencia para obtener el token de autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_token(token: str = Depends(oauth2_scheme)):
    return token