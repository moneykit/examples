from collections import defaultdict

from sqlalchemy.orm import Session

from budgeting_app.users import UserLink

from .models import FinancialAccount, Transaction


class AccountsRepository:
    def __init__(self, db_session: Session) -> None:
        self._db = db_session

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
