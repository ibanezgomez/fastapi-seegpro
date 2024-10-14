import math, traceback
from typing import Any, List, Sequence, Type
from pydantic import BaseModel
from sqlalchemy import func, select, update, not_, delete
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Executable
from sqlalchemy.exc import IntegrityError
from models.base import SQLModel
from fastapi.responses import JSONResponse
 
from utils.endpoint import EndpointInstance
from utils.exceptions import CustomException
from utils.logger import log

from schemas.auth import UserSessionSchema
from schemas.user import UserSchema
from schemas.base import PaginationResult, DeletionResult

from schemas.query_filter import validate_filters

class SessionMixin:
    """Provides instance of database session."""
    def __init__(self, session: Session = None, auth: UserSessionSchema = None, authorization_func: func = None, roles: list = []) -> None:
        self.session = session
        self.auth    = auth
        self.roles   = roles
        if authorization_func != None:
            self.authorization_func = authorization_func
        else:
            self.authorization_func = self.isAllowed

    @staticmethod
    def isAllowed(session: UserSessionSchema):
        if session.user: return True
        else: return False
    
class BaseService(SessionMixin):
    """Base class for application services."""

    def getSchemasFromModels(self, models: Any, schema: Any = None, relation_populate = []) -> List[Any]:
        schemas: List[schema] = list()
        for m in models:
            schemas += [m.to_schema(schema=schema, relation_populate=relation_populate)]
        return schemas

    def FilterValidator(func):
        def wrapper(self, *args, **kwargs):
            if "filters" in kwargs:
                kwargs["filters"] = validate_filters(kwargs["filters"])
            return func(self, *args, **kwargs)

        return wrapper

    def IsAuthenticated(func):
        def wrapper(self, *args, **kwargs):
            if self.auth.user and self.authorization_func(self.auth, self.roles):
                return func(self, *args, **kwargs)
            else:
                raise CustomException(self.auth.errors['detail'], None, self.auth.errors['status_code'])
        return wrapper

    def HTTPExceptionHandler(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                responses=EndpointInstance().getDefaultResponses()
                status_code=500
                data = { 'exception': e.__class__.__name__, 'detail': str(e) }
                if e.__class__ in [ CustomException ]:
                    if e.status_code in responses.keys(): status_code = e.status_code;  data['detail']= e.message
                elif e.__class__ in [ AttributeError ]: 
                    status_code=404; data['detail']="Invalid parameters or data provided."
                elif e.__class__ in [ IntegrityError ]:
                    status_code=409; data['detail']="The object you are trying to add currently exists."
                else: 
                    status_code=500
                
                #Exception controlled
                if status_code != 503:
                    log.error(action="[httpExceptionHandler]", message="Unexpected error. Exception: %s. %s" % (e, traceback.format_exc()))
                return JSONResponse(status_code=status_code, content=responses[status_code]['model'](data=data).dict())
        return wrapper

class BaseDataManager(SessionMixin):
    """Base data manager class responsible for operations over database."""

    #Basic CRUD operations
    def basic_get_one_by_args(self, model: Type[SQLModel], **kwargs):
        stmt = select(model).filter_by(**kwargs)
        model = self.get_one(stmt)
        return model
    
    def basic_get_one_by_id(self, model: Type[SQLModel], id):
        stmt = select(model).where(model.id == id)
        model = self.get_one(stmt)
        return model

    def basic_delete_one_by_id(self, model: Type[SQLModel], id):
        stmt = select(model).where(model.id == id)
        model = self.get_one(stmt)
        if model:
            self.delete_one(model)
            return model
        else:
            raise CustomException(f"{model} with id {id} does not exists", None, 404)
    
    def basic_create_one(self, model: Type[SQLModel], data: BaseModel):
        data_dict = data.model_dump()
        model = model(**data_dict)
        self.add_one(model)
        return model

    def basic_update_full_one_by_id(self, model: Type[SQLModel], id, data: BaseModel):
        stmt = select(model).where(model.id == id)
        model = self.get_one(stmt)
        if model:
            return self.update_one(model, data.model_dump())
        else:
            raise CustomException(f"{model} with id {id} does not exists", None, 404)
    
    def basic_update_partial_one_by_id(self, model: Type[SQLModel], id, data: BaseModel):
        stmt = select(model).where(model.id == id)
        model = self.get_one(stmt)
        if model:
            update_data = self.delete_null_attributes(input_data=data.model_dump())
            return self.update_one(model=model, update_data=update_data)
        else:
            raise CustomException(f"{model} with id {id} does not exists", None, 404)

    def add_one(self, model: Any) -> None:
        self.session.add(model)
        self.session.commit()

    def add_all(self, models: Sequence[Any]) -> None:
        self.session.add_all(models)
        self.session.commit()

    def delete_one(self, model: Any) -> None:
        self.session.delete(model)
        self.session.commit()

    def delete_all(self, model: Any) -> DeletionResult:
        stmt = delete(model)
        result = self.session.execute(stmt)
        self.session.commit()
        return DeletionResult(total_items=result.rowcount)
        
    def update_one(self, model: Any, update_data: dict) -> Any:
        stmt = update(type(model)).where(type(model).id == model.id).values(update_data)
        self.session.execute(stmt)
        self.session.commit()
        return model

    def get_one(self, select_stmt: Executable) -> Any:
        return self.session.scalar(select_stmt)

    def apply_filters(self, query, model, filters_array):
        action = "[apply_filters]"
        try:
            for filter in filters_array:
                column = getattr(model, filter["field"])
                match filter["operator"]:
                    case "==":
                        query = query.filter(column == filter["value"])
                    case "!=":
                        query = query.filter(column != filter["value"])
                    case "contains":
                        query = query.filter(column.ilike("%" + filter["value"] + "%"))
                    case "not_contains":
                        query = query.filter(not_(column.ilike("%" + filter["value"] + "%")))
                    case "<":
                        query = query.filter(column < filter["value"])
                    case "<=":
                        query = query.filter(column <= filter["value"])
                    case ">":
                        query = query.filter(column > filter["value"])
                    case ">=":
                        query = query.filter(column >= filter["value"])
            return query
        except Exception as e:
            log.error(action=action, message=f"Error applying filters. Error: {e}")
            raise CustomException(f"Error applying filters", None, 400)

    def get_paginated(self, model: Type[SQLModel], page: int, per_page: int, filters: List[dict] = None) -> PaginationResult:
        query = self.session.query(model)

        # Aplicar filtros si se proporcionan
        if filters:
            query = self.apply_filters(query, model, filters)

        total_items = query.count()
        total_pages = math.ceil(total_items / per_page)

        paginated_query = query.offset((page - 1) * per_page).limit(per_page)
        items = paginated_query.all()

        return PaginationResult(
            total_items=total_items,
            total_pages=total_pages,
            page=page,
            per_page=per_page,
            items=items
        )

    def get_all(self, select_stmt: Executable) -> List[Any]:
        return list(self.session.scalars(select_stmt).all())

    def get_from_tvf(self, model: Type[SQLModel], *args: Any) -> List[Any]:
        """Query from table valued function.

        This is a wrapper function that can be used to retrieve data from
        table valued functions.

        Examples:
            from app.models.base import SQLModel

            class MyModel(SQLModel):
                __tablename__ = "function"
                __table_args__ = {"schema": "schema"}

                x: Mapped[int] = mapped_column("x", primary_key=True)
                y: Mapped[str] = mapped_column("y")
                z: Mapped[float] = mapped_column("z")

            # equivalent to "SELECT x, y, z FROM schema.function(1, "AAA")"
            BaseDataManager(session).get_from_tvf(MyModel, 1, "AAA")
        """

        fn = getattr(getattr(func, model.schema()), model.table_name())
        stmt = select(fn(*args).table_valued(*model.fields()))
        return self.get_all(select(model).from_statement(stmt))

    # Return JSON without null values
    def delete_null_attributes(self, input_data: dict) -> dict:
        filtered_model = {k: v for k, v in input_data.items() if v is not None}
        return filtered_model

    # Return if is empty or none
    def is_none_or_empty(self, parameter):
        return parameter == None or parameter == ""