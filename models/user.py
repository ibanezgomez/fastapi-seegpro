from sqlalchemy.orm import  Mapped, mapped_column
from datetime import date, datetime
from models.base import SQLModel
from typing import Any

class UserModel(SQLModel):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column("id", primary_key=True)
    name: Mapped[str] = mapped_column("name")
    surname: Mapped[str] = mapped_column("surname")
    roles: Mapped[list[str]] = mapped_column("roles", nullable=False)
    date_created: Mapped[datetime] = mapped_column("date_created", default=datetime.now)
    hashed_password: Mapped[str] = mapped_column("hashed_password")