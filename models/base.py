from typing import Any, Dict, List
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON
from typing import Any
from utils.logger import log

class SQLModel(DeclarativeBase):
    """Base class used for model definitions.
    Provides convenience methods that can be used to convert model
    to the corresponding schema.
    """

    type_annotation_map = {
        dict[str, Any]: JSON
    }

    @classmethod
    def schema(cls) -> str:
        """Return name of database schema the model refers to."""

        _schema = cls.__mapper__.selectable.schema
        if _schema is None:
            raise ValueError("Cannot identify model schema")
        return _schema

    @classmethod
    def table_name(cls) -> str:
        """Return name of the table the model refers to."""

        return cls.__tablename__

    @classmethod
    def fields(cls) -> List[str]:
        """Return list of model field names."""

        return cls.__mapper__.selectable.c.keys()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to a dictionary."""

        _dict: Dict[str, Any] = dict()
        for key in self.__mapper__.c.keys():
            _dict[key] = getattr(self, key)
        return _dict

    def to_schema(self, schema: Any, relation_populate=[]) -> Any:
        """Convert model instance to a dictionary."""

        kwargs = {} 
        for att in relation_populate: 
            populate_model = self.get(att)
            if populate_model: kwargs[att] = populate_model.to_dict()
            else:              kwargs[att] = None

        return schema(**self.to_dict(), **kwargs)

    def to_schema_response(self, schema_response: Any, relation_populate=[]):
        """Convert model instance to a dictionary."""

        data = self.to_dict()
        for att in relation_populate: 
            populate_model = self.get(att)
            if populate_model: data[att] = populate_model.to_dict()
            else:              data[att] = None

        return schema_response(data=data)
    
    def get(self, attribute):
        """Obtain attribute from model."""
        return getattr(self, attribute)

    def __repr__(self):
        class_name = self.__class__.__name__
        fields = ", ".join(f"{key}={value}" for key, value in self.to_dict().items())
        return f"<{class_name}({fields})>"

