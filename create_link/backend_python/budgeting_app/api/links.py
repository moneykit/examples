from datetime import datetime
from typing import Annotated

import pydantic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from budgeting_app.database.connection import get_db_session
from budgeting_app.users import LinkManager, User, UserSessionManager, UsersRepository

router = APIRouter(prefix="/links")


class UserLink(pydantic.BaseModel):
    id: int
    institution_name: str
    state: str


class Institution(pydantic.BaseModel):
    name: str


class Link(pydantic.BaseModel):
    id: int
    updated_at: datetime
    institution: Institution
    state: str


class GetLinksResponse(pydantic.BaseModel):
    links: list[Link]


class DeleteLinkResponse(pydantic.BaseModel):
    pass


class RefreshLinkTransactionsResponse(pydantic.BaseModel):
    pass


@router.get("", response_model=GetLinksResponse)
async def get_links(
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> GetLinksResponse:
    repo = UsersRepository(db_session)
    links = repo.get_links(current_user.id)
    return GetLinksResponse(
        links=[
            Link(
                id=link.id,
                updated_at=link.updated_at,
                institution=Institution(name=link.institution_name),
                state=link.state,
            )
            for link in links
        ]
    )


@router.delete("/{link_id}", response_model=DeleteLinkResponse)
async def delete_link(
    link_id: int,
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> DeleteLinkResponse:
    repo = UsersRepository(db_session)
    link = repo.get_link(current_user.id, link_id)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error_message": "Link not found"})

    LinkManager(db_session).delete_link(link)
    return DeleteLinkResponse()


@router.get("/{link_id}/transactions/refresh", response_model=RefreshLinkTransactionsResponse)
async def refresh_link_transactions(
    link_id: int,
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
) -> RefreshLinkTransactionsResponse:
    repo = UsersRepository(db_session)
    link = repo.get_link(current_user.id, link_id)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error_message": "Link not found"})

    LinkManager(db_session).force_transactions_refresh_for_link(link)
    return RefreshLinkTransactionsResponse()
