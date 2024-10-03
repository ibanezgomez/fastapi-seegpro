from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models.base import SQLModel

class ExampleModel(SQLModel):
    __tablename__ = 'examples'

    id:           Mapped[int] = mapped_column("id", primary_key=True)
    name:         Mapped[str] = mapped_column("name", nullable=False)
    date_created: Mapped[datetime] = mapped_column("date_created", default=datetime.now)
    description:  Mapped[str] = mapped_column("description", nullable=True)
    active:       Mapped[bool] = mapped_column("active", nullable=False, default=True)