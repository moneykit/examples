from __future__ import annotations

import functools
from typing import Annotated
from uuid import uuid4

import moneykit
import moneykit.models
from fastapi import Depends, HTTPException, Request, status
from pydantic import SecretStr
from sqlalchemy.orm import Session

from budgeting_app.database.connection import get_db_session
from budgeting_app.settings import get_settings

from .models import User, UserLink
from .respository import UsersRepository


class UserSessionManager:
    # Non-production login session storage
    def __init__(self) -> None:
        self._user_sessions: dict[str, int] = {}

    def register_new_user(self, db_session: Session, username: str, password: SecretStr) -> tuple[User, str]:
        repo = UsersRepository(db_session)
        user = repo.create_user(username, password)
        db_session.commit()
        session_id = uuid4().hex
        self._user_sessions[session_id] = user.id
        return user, session_id

    def login(self, db_session: Session, username: str, password: SecretStr) -> tuple[User, str]:
        repo = UsersRepository(db_session)
        user = repo.verify_user_password(username, password)
        session_id = uuid4().hex
        self._user_sessions[session_id] = user.id
        return user, session_id

    def get_current_user(self, db_session: Session, session_id: str) -> User | None:
        user_id = self._user_sessions.get(session_id)
        if not user_id:
            return None
        return UsersRepository(db_session).get_user_by_id(user_id)

    def logout_current_user(self, session_id: str) -> None:
        if session_id in self._user_sessions:
            del self._user_sessions[session_id]

    @staticmethod
    @functools.lru_cache
    def get_shared_manager() -> UserSessionManager:
        return UserSessionManager()

    @staticmethod
    def current_user(
        request: Request,
        db_session: Annotated[Session, Depends(get_db_session)],
        user_session_manager: Annotated[UserSessionManager, Depends(UserSessionManager.get_shared_manager)],
    ) -> User:
        session_id = request.cookies.get("session-id")
        if not session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error_message": "Not logged in"})
        user = user_session_manager.get_current_user(db_session, session_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error_message": "Not logged in"})
        return user


class LinkManager:
    def __init__(self, db_session: Session, moneykit_client: moneykit.ApiClient) -> None:
        self._db = db_session
        self._repository = UsersRepository(db_session)
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

    def exchange_token_for_link(self, user: User, exchangeable_token: str) -> UserLink:
        link_session_api = moneykit.LinkSessionApi(self._mk_client)
        exchange_response = link_session_api.exchange_token(
            moneykit.models.ExchangeTokenBody(exchangeable_token=exchangeable_token)
        )
        new_link = UserLink(
            user_id=user.id,
            link_id=exchange_response.link_id,
            state=exchange_response.link.state,
            institution_id=exchange_response.link.institution_id,
            institution_name=exchange_response.link.institution_name,
            transaction_sync_cursor=None,
        )
        self._db.add(new_link)
        self._db.commit()

    def refresh_link(self, link: UserLink) -> UserLink:
        links_api = moneykit.LinksApi(self._mk_client)
        response = links_api.get_link(link.link_id)
        link.state = response.state
        self._db.commit()

    def delete_link(self, link: UserLink) -> None:
        links_api = moneykit.LinksApi(self._mk_client)
        links_api.disconnect(link.link_id)
        self._db.delete(link)
        self._db.commit()

    def sync_latest_transactions_for_link(self, link: UserLink) -> None:
        txns_api = moneykit.TransactionsApi(self._mk_client)

        has_more = True
        next_cursor = link.transaction_sync_cursor

        self._db.begin()

        while has_more:
            response = txns_api.get_transactions_diff(link.id, cursor=next_cursor)
            has_more = response.has_more
            next_cursor = response.cursor
            for created_txn in response.transactions.created:
                # TODO
                pass
            for updated_txn in response.transactions.updated:
                pass
            for removed_txn_id in response.transactions.removed:
                pass

        link.transaction_sync_cursor = next_cursor
        self._db.commit()

    def force_transactions_refresh_for_link(self, link: UserLink) -> None:
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
