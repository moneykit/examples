import logging
from typing import Annotated, Union, cast

import moneykit
import moneykit.models
import pydantic
from fastapi import APIRouter, Header, HTTPException, Request, status

from app.client import MoneyKitWebHookVerificationError, MoneyKitWebHookVerifier, moneykit_client

router = APIRouter(prefix="")
logger = logging.getLogger("example.api.webooks")


AnyWebhook = Annotated[
    Union[
        moneykit.models.LinkProductRefreshWebhook,
        moneykit.models.LinkStateChangedWebhook,
        moneykit.models.TransactionUpdatesAvailableWebhook,
    ],
    # Note this disciminator does not take into account breaking changes (`webhook_major_version`)
    pydantic.Field(discriminator="webhook_event"),
]


@router.post(
    "/webhook-handler",
    status_code=status.HTTP_200_OK,
)
async def handle_moneykit_webhook(
    request: Request,
    moneykit_signature: Annotated[str | None, Header(...)],
    moneykit_delivery_token: Annotated[str | None, Header(...)],
    moneykit_delivery_attempt: Annotated[str | None, Header(...)],
) -> dict:
    """Verifies and handles incoming moneykit webhooks.

    This method should do the least amount of work possible and respond in a timely manner.
    Here we pseudocode triggering Celery background jobs to do the work once the webhook has been verified and decoded.

    `moneykit_delivery_token` and `moneykit_delivery_attempt` can be used to help debug requests and are valuable to
    include in your backend logs.
    """
    # moneykit_signature = request.headers.get("MoneyKit-Signature")
    # moneykit_delivery_token = request.headers.get("MoneyKit-Delivery-Token")
    # moneykit_delivery_attempt = request.headers.get("MoneyKit-Delivery-Attempt")
    logger.info(f"Handling webhook {moneykit_delivery_token=}({moneykit_delivery_attempt}) {moneykit_signature=}")

    body_bytes = await request.body()
    client = moneykit_client()
    try:
        verifier = MoneyKitWebHookVerifier(client)
        verifier.verify_moneykit_webhook_request(moneykit_signature, body_bytes)
    except MoneyKitWebHookVerificationError:
        logger.exception(f"Verification failed {body_bytes=}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "Verification failed"})

    handled = False
    try:
        # Pydantic will correctly deserialize the event body based on the `webhook_event` key.
        body = pydantic.TypeAdapter(AnyWebhook).validate_json(body_bytes)
        logger.info(f"Parsed: {body}")
        match body.webhook_event:
            case "link.state_changed":
                state_changed_webhook = cast(moneykit.models.LinkStateChangedWebhook, body)
                logger.info(
                    f"{state_changed_webhook.link_id}: {state_changed_webhook.state=} "
                    f"{state_changed_webhook.error=} {state_changed_webhook.error_message=}"
                )
                # Next step: start a background job to update the saved link state
                # update_link_state.delay(link_id=state_changed_webhook.link_id)
            case "link.product_refresh":
                product_refresh_webhook = cast(moneykit.models.LinkProductRefreshWebhook, body)
                logger.info(
                    f"{product_refresh_webhook.link_id}: {product_refresh_webhook.product=} "
                    f"{product_refresh_webhook.state=} {product_refresh_webhook.state_changed_at=} "
                    f"{product_refresh_webhook.error_message=}"
                )
                # Next step: start a background job that performs whatever you need after your product has updated
                # do_thing_with_product.delay(link_id=product_refresh_webhook.link_id)
            case "transactions.updates_available":
                transaction_udpates_webhook = cast(moneykit.models.TransactionUpdatesAvailableWebhook, body)
                logger.info(f"{transaction_udpates_webhook.link_id}: {transaction_udpates_webhook.has_history=}")
                # Next step: start a background job that syncs the latest transactions for this link
                # sync_transactions.delay(link_id=transaction_udpates_webhook.link_id)

        handled = True
    except pydantic.ValidationError:
        logger.info(f"Unhandled webhook '{body_bytes}'")

    # Response is only for debugging
    return {"debug_handled": handled}


# @celery.task
# def update_link_state(link_id: str) -> None:
#     # Pseudo code to fetch and store the latest link state in your database
#     link = db.get_link(link_id)
#     links_api = moneykit.LinksApi(moneykit_client())
#     response = links_api.get_link(link_id)
#     link.moneykit_state = response.state.value
#     link.moneykit_error = response.error_code.value
#     link.moneykit_error_message = response.error_message
#     db.commit()


# @celery.task
# def sync_transactions(link_id: str) -> None:
#     # Pseudo code background task to sync transactions to your database
#     link = db.get_link(link_id)
#     transactions_api = moneykit.TransactionsApi(moneykit_client())
#     response = transactions_api.get_transactions_sync(link_id, cursor=link.transaction_sync_cursor)
#     # See `cache_transactions/python` example for how this works
