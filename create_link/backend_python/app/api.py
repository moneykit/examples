from typing import Annotated

import pydantic
from fastapi import APIRouter, Body, status

router = APIRouter(prefix="/linking")


class NewLinkSessionResponse(pydantic.BaseModel):
    link_session_token: str


class ExchangeTokenForLinkRequest(pydantic.BaseModel):
    exchangeable_token: str


class ExchangeTokenForLinkResponse(pydantic.BaseModel):
    moneykit_link_id: str


@router.post("/session", status_code=status.HTTP_201_CREATED, response_model=NewLinkSessionResponse)
async def new_link_session() -> NewLinkSessionResponse:
    return NewLinkSessionResponse(link_session_token="TODO")


@router.post("/exchange-token", status_code=status.HTTP_202_ACCEPTED, response_model=ExchangeTokenForLinkResponse)
async def exchange_token_for_link(
    body: Annotated[ExchangeTokenForLinkRequest, Body()],
) -> ExchangeTokenForLinkResponse:
    moneykit_link_id = "TODO"
    return ExchangeTokenForLinkResponse(moneykit_link_id=moneykit_link_id)
