from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, func

from budgeting_app.database import Base


class FinancialAccount(Base):
    __tablename__ = "financial_accounts"

    id: int = Column(Integer, primary_key=True)
    user_link_id: int = Column(ForeignKey("user_links.id"), nullable=False, index=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    moneykit_id = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False)
    account_type: str = Column(String, nullable=False)
    account_number_masked: str = Column(String, nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"

    id: int = Column(Integer, primary_key=True)
    financial_account_id: int = Column(ForeignKey(FinancialAccount.id), nullable=False, index=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    moneykit_id = Column(String, nullable=False, unique=True)
    description: str = Column(String, nullable=False)
    ammount: Decimal = Column(Numeric(precision=28, scale=10), nullable=False)
    currency: str = Column(String, nullable=False)
    timestamp: date = Column(Date, nullable=False)
    category: str = Column(String, nullable=True)
    pending: bool = Column(Boolean, nullable=False)
