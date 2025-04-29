import logging
from uuid import uuid4

import moneykit
import moneykit.models
from fastapi import APIRouter, status

from app.client import moneykit_client

router = APIRouter(prefix="/links")
logger = logging.getLogger("example.api.links")


@router.post(
    "/{link_id}/refresh/{product}",
    status_code=status.HTTP_200_OK,
)
def refresh_link_product(link_id: str, product: moneykit.models.Product) -> dict:
    """Request a product refresh for a link"""
    products_api = moneykit.ProductsApi(moneykit_client())
    products_api.refresh_products(link_id, moneykit.models.RefreshProductsRequest(products=[product]))
    logger.info(f"Refresh {product}")
    return {}


@router.post(
    "/{link_id}/webhooks/test/state-changed",
    status_code=status.HTTP_200_OK,
)
def trigger_test_state_changed_webhook(link_id: str) -> dict:
    """Trigger a test `link.state_changed` webhook event to be sent by moneykit.
    NOTE: This only works for sandbox links"""
    # You should see this value in the incoming webhook handler
    idempotency_key = str(uuid4())

    webhooks_api = moneykit.WebhooksApi(moneykit_client())
    webhooks_api.trigger_test_link_webhook_event(
        link_id,
        moneykit.models.WebhookTestLinkRequest(
            webhook_event=moneykit.models.WebhookLinkTestEvent.LINK_STATE_CHANGED,
            webhook_idempotency_key=idempotency_key,
        ),
    )
    logger.info(f"Triggered test link.state_changed webhook {idempotency_key=}")
    return {"idempotency_key": idempotency_key}


@router.post(
    "/{link_id}/webhooks/test/product-refresh",
    status_code=status.HTTP_200_OK,
)
def trigger_test_product_refresh_webhook(link_id: str) -> dict:
    """Trigger a test `link.product_refresh` webhook event for `accounts` product to be sent by moneykit.
    NOTE: This only works for sandbox links"""
    idempotency_key = str(uuid4())
    webhooks_api = moneykit.WebhooksApi(moneykit_client())
    thing = moneykit.models.WebhookTestLinkRequest(
        webhook_event=moneykit.models.WebhookLinkTestEvent.LINK_PRODUCT_REFRESH,
        webhook_idempotency_key=idempotency_key,
    )
    webhooks_api.trigger_test_link_webhook_event(
        link_id,
        thing,
    )
    logger.info(f"Triggered test link.product_refresh webhook {idempotency_key=}")
    return {"idempotency_key": idempotency_key}


@router.post(
    "/{link_id}/webhooks/test/transactions-updates",
    status_code=status.HTTP_200_OK,
)
def trigger_test_transactions_updates_webhook(link_id: str) -> dict:
    """Trigger a test `transactions.updates_available` webhook event for product to be sent by moneykit.
    NOTE: This only works for sandbox links"""
    idempotency_key = str(uuid4())
    webhooks_api = moneykit.WebhooksApi(moneykit_client())
    webhooks_api.trigger_test_link_webhook_event(
        link_id,
        moneykit.models.WebhookTestLinkRequest(
            webhook_event=moneykit.models.WebhookLinkTestEvent.TRANSACTIONS_UPDATES_AVAILABLE,
            webhook_idempotency_key=idempotency_key,
        ),
    )
    print(f"Triggered test transactions.updates_available refresh webhook {idempotency_key=}")
    return {"idempotency_key": idempotency_key}


@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_link(link_id: str) -> None:
    """Delete a link"""
    links_api = moneykit.LinksApi(moneykit_client())
    links_api.delete_link(link_id)
    logger.info(f"Deleted link id: {link_id}")
