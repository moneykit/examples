from __future__ import annotations

import functools
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, Request, status
from pydantic import SecretStr
from sqlalchemy.orm import Session

from budgeting_app.database.connection import get_db_session

from .models import User
from .respository import UsersRepository


class UserSessionManager:
    # Non-production login session storage
    def __init__(self) -> None:
        self._user_sessions: dict[str, int] = {}

    def register_new_user(self, db_session: Session, username: str, password: SecretStr) -> tuple[User, str]:
        repo = UsersRepository(db_session)
        user = repo.create_user(username, password)
        db_session.commit()
        session_id = uuid4().hex
        self._user_sessions[session_id] = user.id
        return user, session_id

    def login(self, db_session: Session, username: str, password: SecretStr) -> tuple[User, str]:
        repo = UsersRepository(db_session)
        user = repo.verify_user_password(username, password)
        session_id = uuid4().hex
        self._user_sessions[session_id] = user.id
        return user, session_id

    def get_current_user(self, db_session: Session, session_id: str) -> User | None:
        user_id = self._user_sessions.get(session_id)
        if not user_id:
            return None
        return UsersRepository(db_session).get_user_by_id(user_id)

    def logout_current_user(self, session_id: str) -> None:
        if session_id in self._user_sessions:
            del self._user_sessions[session_id]

    @staticmethod
    @functools.lru_cache
    def get_shared_manager() -> UserSessionManager:
        return UserSessionManager()

    @staticmethod
    def current_user(
        request: Request,
        db_session: Annotated[Session, Depends(get_db_session)],
        user_session_manager: Annotated[UserSessionManager, Depends(UserSessionManager.get_shared_manager)],
    ) -> User:
        session_id = request.cookies.get("session-id")
        if not session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error_message": "Not logged in"})
        user = user_session_manager.get_current_user(db_session, session_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error_message": "Not logged in"})
        return user
