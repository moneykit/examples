import functools
from typing import Annotated

import moneykit
import moneykit.models
import pydantic
from fastapi import APIRouter, Body, status
from moneykit.api.access_token import generate_access_token
from moneykit.api.link_session import create_link_session, exchange_token

from app.settings import get_settings

router = APIRouter(prefix="/linking")


@functools.lru_cache
def create_moneykit_client() -> moneykit.AuthenticatedClient:
    settings = get_settings()
    # Generate a bearer access token that is valid for 60 minutes.
    # This client should be cached to avoid regenerating a token on every request.
    # The bearer token should be regenerated before expiry or after a `api_error.auth.expired_access_token` error code
    # is returned by a request.

    unauthenticated_client = moneykit.Client(base_url=settings.moneykit_url)

    response = generate_access_token.sync(
        client=unauthenticated_client,
        form_data=moneykit.models.BodyGenerateAccessTokenAuthTokenPost(
            grant_type="client_credentials",
            client_id=settings.moneykit_client_id,
            client_secret=settings.moneykit_client_secret.get_secret_value(),
        ),
    )

    client = moneykit.AuthenticatedClient(base_url=settings.moneykit_url, token=response.access_token)
    return client


class NewLinkSessionResponse(pydantic.BaseModel):
    link_session_token: str


class ExchangeTokenForLinkRequest(pydantic.BaseModel):
    exchangeable_token: str


class ExchangeTokenForLinkResponse(pydantic.BaseModel):
    moneykit_link_id: str
    institution_name: str


@router.post("/session", status_code=status.HTTP_201_CREATED, response_model=NewLinkSessionResponse)
async def new_link_session() -> NewLinkSessionResponse:
    client = create_moneykit_client()
    response = create_link_session.sync(
        client=client,
        json_body=moneykit.models.CreateLinkSessionRequest(
            customer_user=moneykit.models.LinkSessionCustomerUser(id="examples-create_link-test-user"),
            link_tags=["examples:create_link"],
            settings=moneykit.models.LinkSessionSettingOverrides(
                link_permissions=moneykit.models.LinkPermissions(
                    requested=[
                        moneykit.models.RequestedLinkPermission(
                            scope=moneykit.models.LinkPermissionScope.ACCOUNTS,
                            reason="play with MoneyKit examples.",
                            required=True,
                        ),
                        moneykit.models.RequestedLinkPermission(
                            scope=moneykit.models.LinkPermissionScope.ACCOUNT_NUMBERS,
                            reason="play with MoneyKit examples.",
                            required=True,
                        ),
                        moneykit.models.RequestedLinkPermission(
                            scope=moneykit.models.LinkPermissionScope.IDENTITY,
                            reason="play with MoneyKit examples.",
                            required=True,
                        ),
                        moneykit.models.RequestedLinkPermission(
                            scope=moneykit.models.LinkPermissionScope.TRANSACTIONS,
                            reason="play with MoneyKit examples.",
                            required=True,
                        ),
                    ]
                ),
                products=moneykit.models.ProductsSettings(
                    account_numbers=moneykit.models.AccountNumbersProductSettings(
                        required=False,
                        prefetch=True,
                    ),
                    identity=moneykit.models.IdentityProductSettings(
                        required=False,
                        prefetch=True,
                    ),
                    transactions=moneykit.models.TransactionsProductSettings(
                        required=False,
                        prefetch=True,
                        extend_history=False,
                    ),
                ),
            ),
        ),
    )
    return NewLinkSessionResponse(link_session_token=response.link_session_token)


@router.post("/exchange-token", status_code=status.HTTP_202_ACCEPTED, response_model=ExchangeTokenForLinkResponse)
async def exchange_token_for_link(
    body: Annotated[ExchangeTokenForLinkRequest, Body()],
) -> ExchangeTokenForLinkResponse:
    client = create_moneykit_client()
    response = exchange_token.sync(
        client=client, json_body=moneykit.models.ExchangeTokenRequest(exchangeable_token=body.exchangeable_token)
    )
    print(f"MoneyKit link id: {response.link_id}")
    return ExchangeTokenForLinkResponse(
        moneykit_link_id=response.link_id,
        institution_name=response.link.institution_name,
    )
