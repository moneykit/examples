import functools
from typing import Annotated

import moneykit.plaid_compatible
import pydantic
from fastapi import APIRouter, Body, status
from moneykit.plaid_compatible.api import plaid_api
from moneykit.plaid_compatible.models import (
    CountryCode,
    Item,
    ItemGetRequest,
    ItemGetResponse,
    ItemPublicTokenExchangeRequest,
    ItemPublicTokenExchangeResponse,
    LinkTokenCreateRequest,
    LinkTokenCreateRequestUser,
    LinkTokenCreateResponse,
    Products,
)

from app.settings import get_settings

router = APIRouter(prefix="/linking")


@functools.lru_cache
def create_moneykit_client() -> plaid_api.PlaidApi:
    settings = get_settings()

    configuration = moneykit.plaid_compatible.Configuration(
        host=settings.moneykit_url + "/plaid-compatible",
        api_key={
            "clientId": settings.moneykit_client_id,
            "secret": settings.moneykit_client_secret.get_secret_value(),
        },
    )
    api_client = moneykit.plaid_compatible.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


class NewLinkTokenResponse(pydantic.BaseModel):
    link_session_token: str


class ExchangeTokenForLinkRequest(pydantic.BaseModel):
    exchangeable_token: str


class ExchangeTokenForLinkResponse(pydantic.BaseModel):
    moneykit_link_id: str
    institution_name: str


@router.post("/session", status_code=status.HTTP_201_CREATED, response_model=NewLinkTokenResponse)
async def new_link_token() -> NewLinkTokenResponse:
    client = create_moneykit_client()

    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="MoneyKit Create Link Example",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id="examples-create_link-test-user"),
    )
    response: LinkTokenCreateResponse = client.link_token_create(request)
    return NewLinkTokenResponse(link_session_token=response.link_token)


@router.post("/exchange-token", status_code=status.HTTP_202_ACCEPTED, response_model=ExchangeTokenForLinkResponse)
async def exchange_token_for_link(
    body: Annotated[ExchangeTokenForLinkRequest, Body()],
) -> ExchangeTokenForLinkResponse:
    client = create_moneykit_client()
    response: ItemPublicTokenExchangeResponse = client.item_public_token_exchange(
        ItemPublicTokenExchangeRequest(public_token=body.exchangeable_token)
    )
    print(f"MoneyKit link id: {response.item_id}, access token: {response.access_token}")

    item_response: ItemGetResponse = client.item_get(ItemGetRequest(access_token=response.access_token))
    item: Item = item_response.item
    institution_id: str = item.institution_id
    # TODO: Fetch institution name

    return ExchangeTokenForLinkResponse(
        moneykit_link_id=response.access_token,
        institution_name=institution_id,
    )
