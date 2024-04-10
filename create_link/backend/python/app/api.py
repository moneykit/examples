import functools
import logging
from typing import Annotated

import moneykit
import moneykit.models
import pydantic
from fastapi import APIRouter, Body, status

from app.settings import get_settings

router = APIRouter()
logger = logging.getLogger("example.api")


@functools.lru_cache
def moneykit_client() -> moneykit.ApiClient:
    """Generates a Bearer token from your client id and secret to access MoneyKit.

    This bearer token will expire. This method does not show regenerating the token on/before expiry for simplicity.

    :returns: An authenticated client
    """
    settings = get_settings()

    # Generate a bearer access token that is valid for 60 minutes.
    # This client _should_ be cached to avoid regenerating a token on every request.
    # The bearer token should be regenerated before expiry or after a `api_error.auth.expired_access_token` error code
    # is returned by a request.

    config = moneykit.Configuration(host=settings.moneykit_url)
    api_client = moneykit.ApiClient(config)

    logger.debug(f"Authenticating to {settings.moneykit_url} as {settings.moneykit_client_id}")
    access_token_api = moneykit.AccessTokenApi(api_client)
    response = access_token_api.generate_access_token(
        client_id=settings.moneykit_client_id,
        client_secret=settings.moneykit_client_secret.get_secret_value(),
        grant_type="client_credentials",
    )

    logger.debug(f"Token will expire in {response.expires_in} seconds")
    api_client.configuration.access_token = response.access_token
    return api_client


class NewLinkSessionResponse(pydantic.BaseModel):
    link_session_token: str


class ExchangeTokenForLinkRequest(pydantic.BaseModel):
    exchangeable_token: str


class ExchangeTokenForLinkResponse(pydantic.BaseModel):
    moneykit_link_id: str
    institution_name: str


@router.post(
    "/linking/session",
    status_code=status.HTTP_201_CREATED,
    response_model=NewLinkSessionResponse,
)
def new_link_session() -> NewLinkSessionResponse:
    """Create a link session. This example shows overriding default settings and products."""
    settings = get_settings()
    link_session_api = moneykit.LinkSessionApi(moneykit_client())

    response = link_session_api.create_link_session(
        moneykit.models.CreateLinkSessionRequest(
            customer_user=moneykit.models.LinkSessionCustomerUser(id="examples-create_link-test-user"),
            link_tags=["examples:create_link"],
            redirect_uri=settings.frontend_oauth_redirect_uri,
            settings=moneykit.models.LinkSessionSettingOverrides(
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
    logger.info("Created a MoneyKit Link Session")
    return NewLinkSessionResponse(link_session_token=response.link_session_token)


@router.post(
    "/linking/exchange-token",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ExchangeTokenForLinkResponse,
)
def exchange_token_for_link(
    body: Annotated[ExchangeTokenForLinkRequest, Body()],
) -> ExchangeTokenForLinkResponse:
    """Exchange the Connect SDK's response for a link_id.

    Note: In real-world applications with a database you should not be exposing moneykit `link_id`s to the clients!
    """
    link_session_api = moneykit.LinkSessionApi(moneykit_client())
    response = link_session_api.exchange_token(
        moneykit.models.ExchangeTokenRequest(exchangeable_token=body.exchangeable_token),
    )
    logger.info(f"MoneyKit link id: {response.link_id}")
    return ExchangeTokenForLinkResponse(
        moneykit_link_id=response.link_id,
        institution_name=response.link.institution_name,
    )


@router.delete(
    "/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def disconnect_link(link_id: str) -> None:
    """Disconnect a link.

    Note: In real-world applications with a database you should not be exposing moneykit `link_id`s to the clients!
    """
    links_api = moneykit.LinksApi(moneykit_client())
    links_api.disconnect(link_id)
    logger.info(f"Disconnected link id: {link_id}")
