import functools
from typing import Annotated

import httpx
import pydantic
from app.settings import get_settings
from fastapi import APIRouter, Body, status

router = APIRouter(prefix="/linking")


def _get_access_token(moneykit_url: str, client_id: str, client_secret: str) -> str:
    try:
        token_request_body = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        response = httpx.post(
            f"{moneykit_url}/auth/token", data=token_request_body, timeout=5
        )
        response.raise_for_status()
        response_body = response.json()
        return response_body["access_token"]
    except httpx.HTTPError as err:
        raise err


@functools.lru_cache
def create_moneykit_client() -> httpx.Client:
    settings = get_settings()
    # Generate a bearer access token that is valid for 60 minutes.
    # This client should be cached to avoid regenerating a token on every request.
    # The bearer token should be regenerated before expiry or after a `api_error.auth.expired_access_token` error code
    # is returned by a request.

    access_token = _get_access_token(
        settings.moneykit_url,
        settings.moneykit_client_id,
        settings.moneykit_client_secret.get_secret_value(),
    )
    client = httpx.Client(
        base_url=settings.moneykit_url,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        timeout=5.0,
    )

    return client


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
async def new_link_session() -> NewLinkSessionResponse:
    client = create_moneykit_client()
    # Prefetch available products for testing.
    response = client.post(
        "/link-session",
        json={
            "customer_user": {"id": "examples-create_link-test-user"},
            "link_tags": ["examples:create_link"],
            "redirect_uri": "https://example.com",
            "settings": {
                "link_permissions": {
                    "requested": [
                        {
                            "scope": "accounts",
                            "reason": "play with MoneyKit examples",
                            "required": True,
                        },
                        {
                            "scope": "account_numbers",
                            "reason": "play with MoneyKit examples",
                            "required": True,
                        },
                        {
                            "scope": "identity",
                            "reason": "play with MoneyKit examples",
                            "required": True,
                        },
                        {
                            "scope": "transactions",
                            "reason": "play with MoneyKit examples",
                            "required": True,
                        },
                    ]
                },
                "products": {
                    "account_numbers": {"required": False, "prefetch": True},
                    "identity": {"required": False, "prefetch": True},
                    "transactions": {"required": False, "prefetch": True},
                },
            },
        },
    )
    response.raise_for_status()
    response_body = response.json()
    link_session_token = response_body["link_session_token"]
    return NewLinkSessionResponse(link_session_token=link_session_token)


@router.post(
    "/exchange-token",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ExchangeTokenForLinkResponse,
)
async def exchange_token_for_link(
    body: Annotated[ExchangeTokenForLinkRequest, Body()],
) -> ExchangeTokenForLinkResponse:
    client = create_moneykit_client()
    response = client.post(
        "/link-session/exchange-token",
        json={
            "exchangeable_token": body.exchangeable_token,
        },
    )
    response.raise_for_status()
    response_body = response.json()
    link_id = response_body["link_id"]
    institution_name = response_body["link"]["institution_name"]

    print(f"MoneyKit link id: {link_id}")
    return ExchangeTokenForLinkResponse(
        moneykit_link_id=link_id,
        institution_name=institution_name,
    )
