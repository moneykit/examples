import logging
from typing import Annotated

import moneykit
import moneykit.models
import pydantic
from fastapi import APIRouter, Body, status

from app.client import moneykit_client
from app.ngrok import get_ngrok_tunnel_to_backend
from app.settings import get_settings

router = APIRouter(prefix="/linking")
logger = logging.getLogger("example.api.linking")


class NewLinkSessionResponse(pydantic.BaseModel):
    link_session_token: str


class ExchangeTokenForLinkRequest(pydantic.BaseModel):
    exchangeable_token: str


class ExchangeTokenForLinkResponse(pydantic.BaseModel):
    moneykit_link_id: str
    institution_name: str


@router.post(
    "/session",
    status_code=status.HTTP_201_CREATED,
    response_model=NewLinkSessionResponse,
)
def new_link_session() -> NewLinkSessionResponse:
    """Create a new link session with a webhook url set to this locally running backend.

    nrgrok is exposing this local service publically so that moneykit.com can send a webhook event.
    """
    settings = get_settings()
    link_session_api = moneykit.LinkSessionApi(moneykit_client())

    # Hint: When deployed you would fetch the url from an environment variable.
    # Do not run ngrok in production-like environments
    backend_url = get_ngrok_tunnel_to_backend()
    webhook_url = f"{backend_url}/webhook-handler"
    logger.info(f"{webhook_url=}")
    logger.info("Navigate to http://localhost:4040/inspect/http to view incoming webhook traffic")

    response = link_session_api.create_link_session(
        moneykit.models.CreateLinkSessionRequest(
            customer_user=moneykit.models.LinkSessionCustomerUser(id="examples-use_webhooks-test-user"),
            link_tags=["examples:use_webhooks"],
            redirect_uri=settings.frontend_oauth_redirect_uri,
            webhook=webhook_url,
            products=moneykit.models.ProductsSettings(
                transactions=moneykit.models.TransactionsProductSettings(
                    required=False,
                    prefetch=True,
                    extend_history=False,
                ),
            ),
        ),
    )
    logger.info("Created a MoneyKit Link Session")
    return NewLinkSessionResponse(link_session_token=response.link_session_token)


@router.post(
    "/exchange-token",
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
