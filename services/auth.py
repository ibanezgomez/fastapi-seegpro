from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer,  OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from fastapi import Request

from models.user import UserModel
from schemas.user import CreateUserSchema, UserSchema
from schemas.auth import TokenSchema, UserSessionSchema
from services.base import BaseDataManager, BaseService
from services.user import pwd_context
from utils.exceptions import CustomException
from schemas.base import SuccessResponse
from utils.enums import AuthStatus
from utils.logger import log
from utils.config import config as cfg

TOKEN = cfg.secrets.shared_seed
API_BASE_PATH = cfg.base_path
TOKEN_TYPE = "bearer"
TOKEN_ALGORITHM = "HS256"

async def get_current_user(request: Request, token: str = Depends(OAuth2PasswordBearer(tokenUrl=API_BASE_PATH + "/login", scheme_name="login"))) -> UserSessionSchema | None:
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
    session = UserSessionSchema(user=None, status=AuthStatus.UNAUTHENTICATED, expires_at=None, errors={ 'exception': 'UnauthorizedResponse', 'detail': 'Unauthorized' })
    if token is None:
        session.errors['detail'] = "Token not provided"
    else:
        try:
            payload = jwt.decode(token, TOKEN, algorithms=[TOKEN_ALGORITHM])
            # extract encoded information
            id: str = payload.get("id")
            desc: str = payload.get("desc")
            provider: str = payload.get("provider") 
            permissions: dict = payload.get("permissions")
            expires_at: str = payload.get("expires_at")
            if id is None:
                session.errors['detail'] = "Invalid credentials. Status: %s" % (session.status.value)
                log.error(action="[get_current_user]", message=session.errors['detail'])
            else:
                session.expires_at=datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                if is_expired(expires_at):
                    session.errors['detail'] = "Token expired. Status: %s" % (session.status.value); session.status=AuthStatus.EXPIRED; 
                    log.error(action="[get_current_user]", message=session.errors['detail'])
                else:
                    session.errors['exception'] = None; 
                    session.status = AuthStatus.AUTHENTICATED; 
                    session.user = UserSchema(id=id, desc=desc, permissions=permissions, provider=provider); 
                    session.errors['detail'] = "Identity: %s. Status: %s. Expires in: %s" % (session.user.id, session.status.value, (datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") - datetime.utcnow().replace(microsecond=0))); 
                    log.debug(action="[get_current_user]", message=session.errors['detail'])
                    request.state.user = session.user
        except JWTError:
            session.errors['detail'] = "Token not valid"; session.status=AuthStatus.INVALID
            log.error(action="[get_current_user]", message="Token not valid. Status: %s" % (session.status.value))
    return session

def validate_roles(session: UserSessionSchema, roles: list):
    if len(roles) == 0:
        return True
    else:
        return any(r in session.user.roles for r in roles)

def is_expired(expires_at: str) -> bool:
    """Return :obj:`True` if token has expired."""
    return datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") < datetime.utcnow()

#class AuthService(HashingMixin, BaseService):
class AuthService(BaseService):
    @BaseService.HTTPExceptionHandler
    def authenticate(self, login: OAuth2PasswordRequestForm = Depends()) -> TokenSchema | None:
        """Generate token.

        Obtains username and password and verifies password against
        hashed password stored in database. If valid then temporary
        token is generated, otherwise the corresponding exception is raised.
        """
        user = AuthDataManager(self.session).get_user(id=login.username)
        if user.hashed_password is None:
            raise CustomException("Incorrect password", None,401)
        else:
            if not pwd_context.verify(login.password, user.hashed_password):
                raise CustomException("Incorrect password", None,401)
            else:
                access_token = self._create_access_token(user)
                return TokenSchema(access_token=access_token, token_type=TOKEN_TYPE)

    def _create_access_token(self, user: UserModel) -> str:
        """Encode user information and expiration time."""
        payload = {
            "sub": user.id, 
            "name": user.name, 
            "surname": user.surname,
            "expires_at": self._expiration_time(), 
            "roles": user.roles
        }
        return jwt.encode(payload, TOKEN, algorithm=TOKEN_ALGORITHM)

    @staticmethod
    def _expiration_time() -> str:
        """Get token expiration time."""
        expires_at = datetime.utcnow() + timedelta(minutes=cfg.db.get("DB_TOKEN_EXPIRATION_TIME"))
        return expires_at.strftime("%Y-%m-%d %H:%M:%S")

class AuthDataManager(BaseDataManager):
    def get_user(self, **kwargs) -> UserModel:
        try:
            stmt = select(UserModel).filter_by(**kwargs)
            model = self.get_one(stmt)
            return model
        except Exception as e:
            raise CustomException("User not found", e, 404)
