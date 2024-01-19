from sqlalchemy.orm import  Mapped, mapped_column
from datetime import date, datetime
from models.base import SQLModel
from typing import Any

class ClientModel(SQLModel):
    __tablename__ = "clients"
    id: Mapped[str] = mapped_column("id", primary_key=True)
    desc: Mapped[str] = mapped_column("desc")
    date_created: Mapped[datetime] = mapped_column("date_created", default=datetime.utcnow)
    provider: Mapped[str] = mapped_column("provider", default='local')
    permissions: Mapped[dict[str, Any]] = mapped_column("extra_fields", nullable=False)
    hashed_password: Mapped[str] = mapped_column("hashed_password")