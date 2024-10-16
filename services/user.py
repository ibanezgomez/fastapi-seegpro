from models.user import UserModel
from schemas.user import CreateUserSchema, UserSchemaResponse, UserSchemaPartialUpdate
from services.base import BaseDataManager, BaseService
from schemas.base import SuccessResponse
from utils.exceptions import CustomException
from utils.crypto import bcrypt_hash, sha512_hash
from sqlalchemy import select

class UserService(BaseService):
    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def create_user(self, user: CreateUserSchema) -> UserSchemaResponse:
        return UserDataManager(self.session).create_user(user).to_schema_response(UserSchemaResponse)

class UserDataManager(BaseDataManager):
    def get_user(self, **kwargs) -> UserModel:
        return self.basic_get_one_by_args(UserModel, **kwargs)
    
    def create_user(self, user: CreateUserSchema) -> UserModel:
        """Add user with hashed password to database."""
        user_dict = user.model_dump()
        del user_dict["password"]
        user_model = UserModel(**user_dict, hashed_password=bcrypt_hash(user.password))
        self.add_one(user_model)
        return user_model
    
    def update_partial_user(self, id: str, data: UserSchemaPartialUpdate) -> UserModel:
        return self.basic_update_partial_one_by_id(UserModel, id, data)