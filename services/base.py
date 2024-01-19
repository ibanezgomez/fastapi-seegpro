from typing import Any, List, Sequence, Type, Optional
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Executable, BinaryExpression
from models.base import SQLModel
import math
from schemas.base import PaginationResult
from fastapi.responses import JSONResponse
from utils.endpoint import EndpointInstance
from sqlalchemy.exc import IntegrityError
import traceback
from utils.exceptions import CustomException
from schemas.auth import ClientSessionSchema, ClientSchema
from utils.logger import log

class SessionMixin:
    """Provides instance of database session."""
    def __init__(self, session: Session = None, auth: ClientSessionSchema = None, authorization_func: func = None) -> None:
        self.session = session
        self.auth    = auth
        if authorization_func != None:
            self.authorization_func = authorization_func
        else:
            self.authorization_func = self.isAllowed

    @staticmethod
    def isAllowed(client: ClientSchema):
        if client: return True
        else: return False
    
class BaseService(SessionMixin):
    """Base class for application services."""

    def getSchemasFromModels(self, models: Any, schema: Any = None, relation_populate = []) -> List[Any]:
        schemas: List[schema] = list()
        for m in models:
            schemas += [m.to_schema(schema=schema, relation_populate=relation_populate)]
        return schemas

    def IsAuthenticated(func):
        def wrapper(self, *args, **kwargs):
            if self.auth.client and self.authorization_func(self.auth.client):
                return func(self, *args, **kwargs)
            else:
                raise CustomException(self.auth.errors['detail'], None, 401)
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

    def add_one(self, model: Any) -> None:
        self.session.add(model)
        self.session.commit()

    def add_all(self, models: Sequence[Any]) -> None:
        self.session.add_all(models)
        self.session.commit()

    def delete_one(self, model: Any) -> None:
        self.session.delete(model)
        self.session.commit()
        
    def update_one(self, model: Any, update_data: dict) -> Any:
        stmt = update(type(model)).where(type(model).id == model.id).values(update_data)
        self.session.execute(stmt)
        self.session.commit()
        return model

    def get_one(self, select_stmt: Executable) -> Any:
        return self.session.scalar(select_stmt)

    def get_paginated(self, model: Type[SQLModel], page: int, per_page: int, filters: Optional[List[BinaryExpression]] = None) -> PaginationResult:
        query = self.session.query(model)

        # Aplicar filtros si se proporcionan
        if filters:
            query = query.filter(*filters)

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

    