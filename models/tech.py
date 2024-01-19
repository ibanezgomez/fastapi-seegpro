from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models.base import SQLModel
from typing import List

class TechModel(SQLModel):
    __tablename__ = 'techs'

    id:           Mapped[str] = mapped_column("id", primary_key=True)
    group:        Mapped[str] = mapped_column("group", nullable=False)
    date_created: Mapped[datetime] = mapped_column("date_created", default=datetime.utcnow)
    default:      Mapped[bool] = mapped_column("default", default=False)