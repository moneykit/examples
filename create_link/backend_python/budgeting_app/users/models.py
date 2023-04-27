from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from budgeting_app.database import Base


class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    id: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    username: str = Column(String, nullable=False, unique=True, index=True)
    password: str = Column(String, nullable=False)
    moneykit_id: str = Column(String, nullable=False, default=lambda: str(uuid4()))


class UserLink(Base):
    __tablename__ = "user_links"

    id: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user_id: int = Column(ForeignKey(User.id), nullable=False, index=True)
    link_id: str = Column(String, nullable=False)
    state: str = Column(String, nullable=False)

    institution_id: str = Column(String, nullable=False)
    institution_name: str = Column(String, nullable=False)
    transaction_sync_cursor: str | None = Column(String, nullable=True)
