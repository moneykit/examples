from datetime import timedelta
from typing import Annotated

import pydantic
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from budgeting_app import users
from budgeting_app.database.connection import get_db_session
from budgeting_app.users.respository import BadUsernameOrPasswordError, UsernameAlreadyExistsError

router = APIRouter(prefix="/user")


class RegisterUserRequest(pydantic.BaseModel):
    username: str
    password: pydantic.SecretStr


class RegisterUserResponse(pydantic.BaseModel):
    user_id: int


class LoginUserRequest(pydantic.BaseModel):
    username: str
    password: pydantic.SecretStr


class LoginUserResponse(pydantic.BaseModel):
    user_id: int


@router.post("/register", response_model=RegisterUserResponse)
async def register_user(
    response: Response,
    body: Annotated[RegisterUserRequest, Body],
    db_session: Annotated[Session, Depends(get_db_session)],
    user_session_manager: Annotated[users.UserSessionManager, Depends(users.UserSessionManager.get_shared_manager)],
) -> RegisterUserResponse:
    try:
        new_user, session_id = user_session_manager.register_new_user(db_session, body.username, body.password)
        response.set_cookie(
            "session-id",
            value=session_id,
            max_age=int(timedelta(minutes=30).total_seconds()),
            samesite="strict",
            httponly=True,
        )
        return RegisterUserResponse(user_id=new_user.id)
    except UsernameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error_message": "Username already exists"}
        )


@router.post("/login", response_model=LoginUserResponse)
async def login_user(
    response: Response,
    body: Annotated[LoginUserRequest, Body],
    db_session: Annotated[Session, Depends(get_db_session)],
    user_session_manager: Annotated[users.UserSessionManager, Depends(users.UserSessionManager.get_shared_manager)],
) -> LoginUserResponse:
    try:
        user, session_id = user_session_manager.login(db_session, body.username, body.password)
        response.set_cookie(
            "session-id",
            value=session_id,
            max_age=int(timedelta(minutes=30).total_seconds()),
            samesite="strict",
            httponly=True,
        )
        return LoginUserResponse(user_id=user.id)
    except BadUsernameOrPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error_message": "Bad username or password"}
        )


@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    current_user: Annotated[users.User, Depends(users.UserSessionManager.current_user)],
    user_session_manager: Annotated[users.UserSessionManager, Depends(users.UserSessionManager.get_shared_manager)],
) -> dict:
    session_id = request.cookies.get("session-id")
    if session_id:
        user_session_manager.logout_current_user(session_id)
    response.delete_cookie("session-id", samesite="strict", httponly=True)
    return {}
