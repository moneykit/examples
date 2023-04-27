from collections import defaultdict
from datetime import date
from decimal import Decimal

import sqlalchemy
from sqlalchemy.orm import Session

from budgeting_app.users import UserLink

from .models import FinancialAccount, Transaction


class AccountsRepository:
    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def new_account(
        self, link_id: int, moneykit_account_id: str, name: str, account_type: str, account_number_masked: str | None
    ) -> FinancialAccount:
        account = FinancialAccount(
            user_link_id=link_id,
            moneykit_id=moneykit_account_id,
            name=name,
            account_type=account_type,
            account_number_masked=account_number_masked,
        )
        self._db.add(account)
        return account

    def new_transaction(
        self,
        account_id: int,
        moneykit_transaction_id: str,
        description: str,
        amount: Decimal,
        currency: str | None,
        timestamp: date,
        category: str | None,
        pending: bool,
    ) -> Transaction:
        new_txn = Transaction(
            financial_account_id=account_id,
            moneykit_id=moneykit_transaction_id,
            description=description,
            amount=amount,
            currency=currency,
            timestamp=timestamp,
            category=category,
            pending=pending,
        )
        self._db.add(new_txn)
        return new_txn

    def update_transaction(
        self,
        moneykit_transaction_id: str,
        description: str,
        amount: Decimal,
        currency: str | None,
        timestamp: date,
        category: str | None,
        pending: bool,
    ) -> Transaction:
        existing_txn = self._db.query(Transaction).filter(Transaction.moneykit_id == moneykit_transaction_id).one()
        rebuilt_txn = Transaction(
            id=existing_txn.id,  # Naive overwrite on merge
            financial_account_id=existing_txn.financial_account_id,
            moneykit_id=moneykit_transaction_id,
            description=description,
            amount=amount,
            currency=currency,
            timestamp=timestamp,
            category=category,
            pending=pending,
        )
        self._db.merge(rebuilt_txn)

    def delete_transaction_by_mk_id(self, moneykit_transaction_id: str) -> None:
        self._db.execute(sqlalchemy.delete(Transaction).where(Transaction.moneykit_id == moneykit_transaction_id))

    def get_moneykit_ids_for_link_accounts(self, link_id: int) -> dict[str, int]:
        """Get a map of moneykit_id to FinancialAccount.id for a link id"""
        accounts: list[FinancialAccount] = (
            self._db.query(FinancialAccount)
            .join(UserLink)
            .filter(UserLink.link_id == link_id)
            .order_by(FinancialAccount.created_at, FinancialAccount.id)
            .all()
        )
        by_moneykit_id: dict[str, str] = {}
        for account in accounts:
            by_moneykit_id[account.moneykit_id].append(account.id)

        return by_moneykit_id

    def get_all_accounts(self, user_id: int) -> dict[int, list[FinancialAccount]]:
        """Get all accounts for a user grouped by link id"""
        accounts: list[FinancialAccount] = (
            self._db.query(FinancialAccount)
            .join(UserLink)
            .filter(UserLink.user_id == user_id)
            .order_by(FinancialAccount.created_at, FinancialAccount.id)
            .all()
        )
        by_link_id: dict[int, list[FinancialAccount]] = defaultdict(list)
        for account in accounts:
            by_link_id[account.user_link_id].append(account)

        return by_link_id

    def get_account(self, user_id: int, account_id: int) -> FinancialAccount | None:
        """Get an account for a specific link"""
        account: FinancialAccount | None = (
            self._db.query(FinancialAccount)
            .join(UserLink)
            .filter(UserLink.user_id == user_id, FinancialAccount.id == account_id)
            .one_or_none()
        )
        return account

    def get_transactions_for_account(self, user_id: int, account_id: int) -> list[Transaction]:
        """Get all transactions on a specific account"""
        # TODO: Paginate
        transactions: list[Transaction] = (
            self._db.query(Transaction)
            .join(FinancialAccount)
            .join(UserLink)
            .filter(UserLink.user_id == user_id, FinancialAccount.id == account_id)
            .order_by(Transaction.timestamp.desc(), Transaction.id.desc())
            .all()
        )
        return transactions
