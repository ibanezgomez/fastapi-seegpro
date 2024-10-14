from passlib.context import CryptContext
from models.user import UserModel
from schemas.user import CreateUserSchema, UserSchemaResponse
from services.base import BaseDataManager, BaseService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(BaseService):
    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def create_user(self, user: CreateUserSchema) -> UserSchemaResponse:
        return UserDataManager(self.session).create_user(user).to_schema_response(UserSchemaResponse)

class UserDataManager(BaseDataManager):
    def create_user(self, user: CreateUserSchema) -> UserModel:
        """Add user with hashed password to database."""
        user_dict = user.model_dump()
        del user_dict["password"]
        user_model = UserModel(**user_dict, hashed_password=pwd_context.hash(user.password))
        self.add_one(user_model)
        return user_model