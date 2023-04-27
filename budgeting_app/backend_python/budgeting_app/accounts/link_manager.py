from __future__ import annotations

import functools
from decimal import Decimal

import moneykit
import moneykit.models
from sqlalchemy.orm import Session

from budgeting_app.backend_python.budgeting_app.accounts.respository import AccountsRepository
from budgeting_app.backend_python.budgeting_app.users.respository import UsersRepository
from budgeting_app.settings import get_settings
from budgeting_app.users.models import User, UserLink


class LinkManager:
    def __init__(self, db_session: Session, moneykit_client: moneykit.ApiClient) -> None:
        self._db = db_session
        self._mk_client = moneykit_client

    def start_new_link_session(self, user: User) -> str:
        """Create a new link session and return the link session token."""
        link_session_api = moneykit.LinkSessionApi(self._mk_client)
        response = link_session_api.create_link_session(
            moneykit.models.CreateLinkSessionBody(
                customer_user=moneykit.models.CustomerUser(id=user.moneykit_id),
                link_tags=["examples:budgeting_app"],
                settings=moneykit.models.Settings(
                    link_permissions=moneykit.models.LinkPermissions(
                        requested=[
                            moneykit.models.RequestedLinkPermission(
                                scope=moneykit.models.LinkPermissionScope.TRANSACTIONS,
                                reason="show a breakdown of your spending.",
                                required=True,
                            )
                        ]
                    ),
                    # TODO: Fix API spec naming
                    products=moneykit.models.Products1(
                        transactions=moneykit.models.Transactions(
                            required=True,
                            prefetch=True,
                            extend_history=False,
                        )
                    ),
                ),
            )
        )
        return response.link_session_token

    def complete_linking_process(self, user: User, exchangeable_token: str) -> UserLink:
        """Exchange token from MoneyLink SDK completion and create a UserLink"""
        link_session_api = moneykit.LinkSessionApi(self._mk_client)
        exchange_response = link_session_api.exchange_token(
            moneykit.models.ExchangeTokenBody(exchangeable_token=exchangeable_token)
        )

        users_repo = UsersRepository(self._db)
        new_link = users_repo.create_link(
            user_id=user.id,
            mnoneykit_link_id=exchange_response.link_id,
            state=exchange_response.link.state,
            institution_id=exchange_response.link.institution_id,
            institution_name=exchange_response.link.institution_name,
        )
        self._db.commit()

        accounts_api = moneykit.AccountsApi(self._mk_client)
        accounts_response = accounts_api.get_accounts(new_link.link_id)
        accounts_repo = AccountsRepository(self._db)
        for account in accounts_response.accounts:
            accounts_repo.new_account(
                link_id=new_link.id,
                moneykit_account_id=account.account_id,
                name=account.name,
                account_type=account.account_type.value,
                account_number_masked=account.account_mask,
            )
        self._db.commit()

    def refresh_link(self, link: UserLink) -> UserLink:
        """Manually check the link's state"""
        links_api = moneykit.LinksApi(self._mk_client)
        response = links_api.get_link(link.link_id)
        link.state = response.state
        self._db.commit()

    def delete_link(self, link: UserLink) -> None:
        """Disconnect the link and remove from the database"""
        links_api = moneykit.LinksApi(self._mk_client)
        links_api.disconnect(link.link_id)
        users_repo = UsersRepository(self._db)
        users_repo.delete_link(link.id)
        self._db.commit()

    def sync_latest_transactions_for_link(self, link: UserLink) -> None:
        """Fetch the latest transaction updates and apply to the database"""
        txns_api = moneykit.TransactionsApi(self._mk_client)

        self._db.begin()
        self._db.refresh(link)

        has_more = True
        next_cursor = link.transaction_sync_cursor

        accounts_repo = AccountsRepository(self._db)
        account_id_lookup = accounts_repo.get_moneykit_ids_for_link_accounts(link.id)

        while has_more:
            response = txns_api.get_transactions_diff(link.id, cursor=next_cursor)
            has_more = response.has_more
            next_cursor = response.cursor
            for created_txn in response.transactions.created:
                moneykit_account_id = created_txn.account_id
                account_id = account_id_lookup[moneykit_account_id]

                accounts_repo.new_transaction(
                    account_id=account_id,
                    moneykit_transaction_id=created_txn.transaction_id,
                    description=created_txn.description,
                    amount=Decimal(created_txn.amount),  # TODO: Adjust generated sdk to make Decimal
                    currency=created_txn.currency,
                    timestamp=created_txn.var_date,  # TODO: Fix this generated name
                    category=created_txn.category,
                    pending=created_txn.pending,
                )
            for updated_txn in response.transactions.updated:
                accounts_repo.update_transaction(
                    moneykit_transaction_id=updated_txn.transaction_id,
                    description=created_txn.description,
                    amount=Decimal(created_txn.amount),  # TODO: Adjust generated sdk to make Decimal
                    currency=created_txn.currency,
                    timestamp=created_txn.var_date,  # TODO: Fix this generated name
                    category=created_txn.category,
                    pending=created_txn.pending,
                )
            for removed_txn_id in response.transactions.removed:
                accounts_repo.delete_transaction_by_mk_id(removed_txn_id)

        link.transaction_sync_cursor = next_cursor
        self._db.commit()

    def force_transactions_refresh_for_link(self, link: UserLink) -> None:
        """Schedule fetching new transaction data. MoneyKit will trigger a webhook if/when fresh transactions are
        available. You can then use `sync_latest_transactions_for_link` to fetch the new data.
        """
        products_api = moneykit.ProductsApi(self._mk_client)
        products_api.refresh_products(
            link.id,
            moneykit.models.RefreshProductsBody(products=[moneykit.models.Product.TRANSACTIONS]),
        )


@functools.lru_cache
def create_moneykit_client() -> moneykit.ApiClient:
    # TODO: Fix
    settings = get_settings()
    # Generate a bearer access token that is valid for 60 minutes.
    unauthenticated_client = moneykit.ApiClient(configuration=moneykit.Configuration(host=settings.moneykit_url))
    response = moneykit.AccessTokenApi(unauthenticated_client).generate_access_token(
        grant_type="client_credentials",
        client_id=settings.moneykit_client_id,
        client_secret=settings.moneykit_client_secret.get_secret_value(),
    )

    config = moneykit.Configuration(host=settings.moneykit_url)
    config.access_token = response.access_token  # Bug with constructor overwriting to `None`
    client = moneykit.ApiClient(configuration=config)
    return client
