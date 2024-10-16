from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ARRAY, String
from datetime import datetime
from models.base import SQLModel
from typing import Any

class UserModel(SQLModel):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column("id", primary_key=True)
    name: Mapped[str] = mapped_column("name", nullable=False)
    surname: Mapped[str] = mapped_column("surname", nullable=False)
    roles: Mapped[list[str]] = mapped_column("roles", ARRAY(String), nullable=False)
    date_created: Mapped[datetime] = mapped_column("date_created", default=datetime.now)
    hashed_password: Mapped[str] = mapped_column("hashed_password", nullable=False)
    biometric_challenge: Mapped[str] = mapped_column("biometric_challenge", nullable=True, unique=True)
    biometric_credential: Mapped[str] = mapped_column("biometric_credential", nullable=True)