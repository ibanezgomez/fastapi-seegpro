from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer,  OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from fastapi import Request

from models.client import ClientModel
from schemas.auth import CreateClientSchema, TokenSchema, ClientSchema, ClientSessionSchema
from services.base import BaseDataManager, BaseService
from utils.exceptions import CustomException
from schemas.base import SuccessResponse
from utils.enums import AuthStatus
from utils.logger import log
from utils.config import config as cfg


TOKEN = cfg.secrets.shared_seed
API_BASE_PATH = cfg.base_path
TOKEN_TYPE = "bearer"
TOKEN_ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_client(request: Request, token: str = Depends(OAuth2PasswordBearer(tokenUrl=API_BASE_PATH + "/token-local", scheme_name="local_oauth2_schema"))) -> ClientSessionSchema | None:
    """Decode token to obtain client information.

    Extracts client information from token and verifies expiration time.
    If token is valid then instance of :class:`~app.schemas.auth.ClientSchema`
    is returned, otherwise exception is raised.

    Args:
        token:
            The token to verify.

    Returns:
        Decoded client dictionary.
    """
    client_session = ClientSessionSchema(client=None, status=AuthStatus.UNAUTHENTICATED, expires_at=None, errors={ 'exception': 'UnauthorizedResponse', 'detail': 'Unauthorized' })
    if token is None:
        client_session.errors['detail'] = "Token not provided"
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
                client_session.errors['detail'] = "Invalid credentials. Status: %s" % (client_session.status.value)
                log.error(action="[get_current_client]", message=client_session.errors['detail'])
            else:
                client_session.expires_at=datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                if is_expired(expires_at):
                    client_session.errors['detail'] = "Token expired. Status: %s" % (client_session.status.value); client_session.status=AuthStatus.EXPIRED; 
                    log.error(action="[get_current_client]", message=client_session.errors['detail'])
                else:
                    client_session.errors['exception'] = None; 
                    client_session.status=AuthStatus.AUTHENTICATED; 
                    client_session.client=ClientSchema(id=id, desc=desc, permissions=permissions, provider=provider); 
                    client_session.errors['detail'] = "Identity: %s. Status: %s. Expires in: %s" % (client_session.client.id, client_session.status.value, (datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") - datetime.utcnow().replace(microsecond=0))); 
                    log.debug(action="[get_current_client]", message=client_session.errors['detail'])
                    request.state.client=client_session.client
        except JWTError:
            client_session.errors['detail'] = "Token not valid"; client_session.status=AuthStatus.INVALID
            log.error(action="[get_current_client]", message="Token not valid. Status: %s" % (client_session.status.value))
    return client_session

def is_expired(expires_at: str) -> bool:
    """Return :obj:`True` if token has expired."""
    return datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") < datetime.utcnow()

#class AuthService(HashingMixin, BaseService):
class AuthService(BaseService):
    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def create_client(self, client: CreateClientSchema) -> None:
        """Add client with hashed password to database."""
        client_model = ClientModel(id=client.id, desc=client.desc, provider="local", permissions=client.permissions, hashed_password=pwd_context.hash(client.password))
        AuthDataManager(self.session).add_client(client_model)
        return SuccessResponse(message="Created!", data={"id":client.id, "desc":client.desc})

    @BaseService.HTTPExceptionHandler
    def authenticate(self, login: OAuth2PasswordRequestForm = Depends()) -> TokenSchema | None:
        """Generate token.

        Obtains username and password and verifies password against
        hashed password stored in database. If valid then temporary
        token is generated, otherwise the corresponding exception is raised.
        """
        client = AuthDataManager(self.session).get_client(id=login.username)
        if client.hashed_password is None:
            raise CustomException("Incorrect password", None,401)
        else:
            if not pwd_context.verify(login.password, client.hashed_password):
                raise CustomException("Incorrect password", None,401)
            else:
                access_token = self._create_access_token(client.id, client.desc, client.permissions, client.provider)
                return TokenSchema(access_token=access_token, token_type=TOKEN_TYPE)

    def _create_access_token(self, id: str, desc: str, permissions: dict, provider: str) -> str:
        """Encode client information and expiration time."""
        payload = {"id": id, "desc": desc, "permissions": permissions,"expires_at": self._expiration_time(), "provider": provider}
        return jwt.encode(payload, TOKEN, algorithm=TOKEN_ALGORITHM)

    @staticmethod
    def _expiration_time() -> str:
        """Get token expiration time."""
        expires_at = datetime.utcnow() + timedelta(minutes=cfg.db.get("DB_TOKEN_EXPIRATION_TIME"))
        return expires_at.strftime("%Y-%m-%d %H:%M:%S")

class AuthDataManager(BaseDataManager):
    def add_client(self, client: ClientModel) -> None:
        """Write client to database."""
        client.date_created = datetime.utcnow()
        client.provider = 'local'
        self.add_one(client)

    def get_client(self, **kwargs) -> ClientSchema:
        try:
            stmt = select(ClientModel).filter_by(**kwargs)
            model = self.get_one(stmt)
            return ClientSchema(id=model.id, desc=model.desc, date_created=model.date_created, provider=model.provider, permissions=model.permissions, hashed_password=model.hashed_password )
        except Exception as e:
            raise CustomException("Client not found", e, 404)
