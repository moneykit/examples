import functools
from typing import Annotated

import moneykit
import moneykit.models
import pydantic
from fastapi import APIRouter, Body, status

from app.settings import get_settings

router = APIRouter(prefix="/linking")


@functools.lru_cache
def create_moneykit_client() -> moneykit.ApiClient:
    settings = get_settings()
    # Generate a bearer access token that is valid for 60 minutes.
    # This client should be cached to avoid regenerating a token on every request.
    # The bearer token should be regenerated before expiry or after a `api_error.auth.expired_access_token` error code
    # is returned by a request.
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
    link_session_api = moneykit.LinkSessionApi(client)
    response = link_session_api.create_link_session(
        moneykit.models.CreateLinkSessionBody(
            customer_user=moneykit.models.CustomerUser(id="examples-create_link-test-user"),
            link_tags=["examples:create_link"],
            settings=moneykit.models.SettingOverrides(
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
                # TODO: Fix API spec naming
                products=moneykit.models.Products1(
                    account_numbers=moneykit.models.AccountNumbers(
                        required=False,
                        prefetch=True,
                    ),
                    identity=moneykit.models.Identity(
                        required=False,
                        prefetch=True,
                    ),
                    transactions=moneykit.models.Transactions(
                        required=False,
                        prefetch=True,
                        extend_history=False,
                    ),
                ),
            ),
        )
    )
    return NewLinkSessionResponse(link_session_token=response.link_session_token)


@router.post("/exchange-token", status_code=status.HTTP_202_ACCEPTED, response_model=ExchangeTokenForLinkResponse)
async def exchange_token_for_link(
    body: Annotated[ExchangeTokenForLinkRequest, Body()],
) -> ExchangeTokenForLinkResponse:
    client = create_moneykit_client()
    link_session_api = moneykit.LinkSessionApi(client)
    response = link_session_api.exchange_token(
        moneykit.models.ExchangeTokenBody(exchangeable_token=body.exchangeable_token)
    )
    print(f"MoneyKit link id: {response.link_id}")
    return ExchangeTokenForLinkResponse(
        moneykit_link_id=response.link_id,
        institution_name=response.link.institution_name,
    )
