from datetime import datetime

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

engine = create_engine("postgresql://postgres:password@db", echo=False)


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    moneykit_id: Mapped[str] = mapped_column(unique=True)
    transaction_sync_cursor: Mapped[str | None]

    def __repr__(self) -> str:
        return (
            f'Link(id={self.id}, moneykit_id="{self.moneykit_id}", '
            f'transaction_sync_cursor="{self.transaction_sync_cursor}")'
        )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id"))

    moneykit_id: Mapped[str] = mapped_column(unique=True)
    timestamp: Mapped[datetime]
    description: Mapped[str | None]
    pending: Mapped[bool]

    link: Mapped["Link"] = relationship()

    def __repr__(self) -> str:
        return (
            f'Transaction(id={self.id}, moneykit_id="{self.moneykit_id}", timestamp={self.timestamp}, '
            f'description="{self.description}", pending={self.pending})'
        )
