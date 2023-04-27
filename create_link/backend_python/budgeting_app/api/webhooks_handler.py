import json
import logging
from datetime import datetime
from typing import Annotated, Literal

import pydantic
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from . import webhook_verification

router = APIRouter(prefix="/moneykit-webhooks")
logger = logging.getLogger(__name__)


class NewLinkSessionResponse(pydantic.BaseModel):
    pass


class ExchangeTokenForLinkRequest(pydantic.BaseModel):
    exchangeable_token: str


class ExchangeTokenForLinkResponse(pydantic.BaseModel):
    pass


@router.post("/session", status_code=status.HTTP_202_ACCEPTED)
async def new_link_session() -> NewLinkSessionResponse:
    raise NotImplementedError


@router.post("/exchange-token", status_code=status.HTTP_201_CREATED)
class LinkStateChangedWebhook(pydantic.BaseModel):
    webhook_event: Literal["link.state_changed"] = "link.state_changed"
    webhook_major_version: int
    webhook_minor_version: int

    webhook_idempotency_key: str
    webhook_timestamp: datetime

    link_id: str
    link_tags: list[str]

    # state: mk_models.LinkState
    # error: mk_models.LinkError | None
    # error_message: str | None


@router.post("")
async def handle_webhook_event(
    request: Request,
    verifier: Annotated[webhook_verification.MoneyKitWebHookVerifier, Depends(webhook_verification.get_verifier)],
    moneykit_signature: Annotated[str | None, Header()] = None,
    user_agent: Annotated[str | None, Header()] = None,
) -> dict:
    moneykit_delivery_token = request.headers.get("MoneyKit-Delivery-Token")
    logger.info(f"Webhook event for {user_agent=} {moneykit_delivery_token=} {moneykit_signature=}")

    data_bytes = await request.body()
    try:
        verifier.verify_moneykit_webhook(moneykit_signature, data_bytes)
    except webhook_verification.MoneyKitWebHookVerificationError:
        logger.exception("Verification failed")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "Verification failed"})

    body = json.loads(data_bytes.decode("utf-8"))
    event = body.get("webhook_event")
    if not event:
        logger.error(f"Invalid webhook shape '{body}'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "Missing event type key"})

    match event:
        case "link.state_changed":
            link_state_changed = LinkStateChangedWebhook.parse_obj(body)
            logger.info(f"Webhook handled {link_state_changed}")
        case _:
            logger.warning(f"Unhandled webhook '{body}'")

    return {}
