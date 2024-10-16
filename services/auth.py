from datetime import datetime, timedelta
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer,  OAuth2PasswordRequestForm
from jose import jwt, JWTError
from typing import Optional
from fastapi import Response
from models.user import UserModel
from schemas.user import UserSchema
from schemas.auth import TokenSchema, UserSessionSchema, LoginSchema
from services.base import BaseService
from services.user import UserDataManager
from utils.crypto import bcrypt_verify
from utils.exceptions import CustomException
from utils.enums import AuthStatus
from utils.logger import log
from utils.config import config as cfg

TOKEN = cfg.secrets.shared_seed
API_BASE_PATH = cfg.base_path
TOKEN_TYPE = "bearer"
TOKEN_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=API_BASE_PATH + "/login-form", scheme_name="login", auto_error=False)

async def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> UserSessionSchema | None:
    """Decode token to obtain user information.

    Extracts user information from token and verifies expiration time.
    If token is valid then instance of :class:`~app.schemas.user.UserSchema`
    is returned, otherwise exception is raised.

    Args:
        token:
            The token to verify.

    Returns:
        Decoded user dictionary.
    """
    session = UserSessionSchema(user=None, status=AuthStatus.UNAUTHENTICATED, expires_at=None, errors={ 'detail': '' })

    if token is None:
        session.errors['detail'] = "Token not provided"
        session.status = AuthStatus.UNAUTHENTICATED
        session.errors['status_code'] = 401
    else:
        try:
            payload = jwt.decode(token, TOKEN, algorithms=[TOKEN_ALGORITHM])

            # extract encoded information
            sub: str = payload.get("sub")
            expires_at: str = payload.get("expires_at")

            if sub is None:
                session.errors['detail'] = "Token not valid"
                session.status = AuthStatus.INVALID
                session.errors['status_code'] = 401
            else:
                session.expires_at = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                if is_expired(expires_at):
                    session.errors['detail'] = "Token expired"
                    session.status = AuthStatus.EXPIRED
                    session.errors['status_code'] = 401
                else:
                    session.status = AuthStatus.AUTHENTICATED
                    session.user = UserSchema(**payload, id=sub)
                    log_message = "Identity: %s. Status: %s. Expires in: %s" % (session.user.id, session.status.value, (datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") - datetime.utcnow().replace(microsecond=0)))
                    request.state.user = session.user
                    log.info(action="[get_current_user]", message=log_message)
        except JWTError:
            session.errors['detail'] = "Token not valid"
            session.status=AuthStatus.INVALID
            session.errors['status_code'] = 401
            log.error(action="[get_current_user]", message="Token not valid. Status: %s" % (session.status.value))
    
    if session.status != AuthStatus.AUTHENTICATED:
        log.error(action="[get_current_user]", message="Status: " + session.status + " - Detail: " + session.errors['detail'])

    return session

def validate_roles(session: UserSessionSchema, roles: list):
    if len(roles) == 0:
        return True
    else:
        if any(r in session.user.roles for r in roles):
            return True
        else:
            session.errors['detail'] = "Access Denieds"
            session.status=AuthStatus.FORBIDDEN
            session.errors['status_code'] = 403
            log.error(action="[validate_roles]", message="Status: " + session.status + " - Detail: " + session.errors['detail'])
            return

def is_expired(expires_at: str) -> bool:
    """Return :obj:`True` if token has expired."""
    return datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") < datetime.now()

#class AuthService(HashingMixin, BaseService):
class AuthService(BaseService):
    @BaseService.HTTPExceptionHandler
    def authenticate(self, response: Response, login: LoginSchema) -> TokenSchema | None:
        user = UserDataManager(self.session).get_user(id=login.username)
        if user == None:
            log.error(action="[authenticate]", message="User not found", user=login.username)
            raise CustomException("Incorrect credentials", None, 401)
        
        if not bcrypt_verify(login.password, user.hashed_password):
            log.error(action="[authenticate]", message="Invalid password", user=login.username)
            raise CustomException("Incorrect credentials", None,401)
        else:
            return self._create_access_token(response, user)

    def _create_access_token(self, response: Response, user: UserModel) -> str:
        """Encode user information and expiration time."""
        payload = {
            "sub": user.id, 
            "name": user.name, 
            "surname": user.surname,
            "expires_at": self._expiration_time(), 
            "roles": user.roles
        }
        token = jwt.encode(payload, TOKEN, algorithm=TOKEN_ALGORITHM)

        #Add as header also for FWK Front
        response.headers["Authorization"] = token
        response.headers["Access-Control-Expose-Headers"] = "Authorization"

        return TokenSchema(access_token=token, token_type=TOKEN_TYPE)

    @staticmethod
    def _expiration_time() -> str:
        """Get token expiration time."""
        expires_at = datetime.now() + timedelta(minutes=cfg.db.get("DB_TOKEN_EXPIRATION_TIME"))
        return expires_at.strftime("%Y-%m-%d %H:%M:%S")    