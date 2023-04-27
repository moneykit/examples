from typing import Annotated

import pydantic
from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from budgeting_app.database.connection import get_db_session
from budgeting_app.users import LinkManager, User, UserSessionManager

router = APIRouter(prefix="/linking")


class NewLinkSessionResponse(pydantic.BaseModel):
    link_session_token: str


class ExchangeTokenForLinkRequest(pydantic.BaseModel):
    exchangeable_token: str


class ExchangeTokenForLinkResponse(pydantic.BaseModel):
    user_link_id: int
    transaction_data_available: bool
    all_transaction_data_ready: bool


@router.post("/session", status_code=status.HTTP_201_CREATED, response_model=NewLinkSessionResponse)
async def new_link_session(
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> NewLinkSessionResponse:
    manager = LinkManager(db_session)
    link_session_token = manager.start_new_link_session(current_user)
    return NewLinkSessionResponse(link_session_token=link_session_token)


@router.post("/exchange-token", status_code=status.HTTP_202_ACCEPTED, response_model=ExchangeTokenForLinkResponse)
async def exchange_token_for_link(
    body: Annotated[ExchangeTokenForLinkRequest, Body()],
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> ExchangeTokenForLinkResponse:
    manager = LinkManager(db_session)
    link = manager.exchange_token_for_link(current_user, body.exchangeable_token)
    return ExchangeTokenForLinkResponse(
        user_link_id=link.id,
        transaction_data_available=False,
        all_transaction_data_ready=False,
    )
