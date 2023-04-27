import sqlalchemy
from passlib.hash import pbkdf2_sha256
from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import User, UserLink


class UsernameAlreadyExistsError(Exception):
    pass


class BadUsernameOrPasswordError(Exception):
    pass


class UsersRepository:
    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def create_user(self, username: str, password: SecretStr) -> User:
        hashed_password = pbkdf2_sha256.hash(password.get_secret_value())
        user = User(username=username, password=hashed_password)
        try:
            self._db.add(user)
            self._db.flush()
        except IntegrityError:
            raise UsernameAlreadyExistsError()

        return user

    def verify_user_password(self, username: str, password: SecretStr) -> User:
        if not username:
            raise BadUsernameOrPasswordError()

        user: User | None = self._db.query(User).filter(User.username == username).one_or_none()
        if not user:
            raise BadUsernameOrPasswordError()

        if not pbkdf2_sha256.verify(password.get_secret_value(), hash=user.password):
            raise BadUsernameOrPasswordError()

        return user

    def get_user_by_username(self, username: str) -> User | None:
        if not username:
            None

        user: User | None = self._db.query(User).filter(User.username == username).one_or_none()
        return user

    def get_user_by_id(self, id: int) -> User | None:
        user: User | None = self._db.query(User).filter(User.id == id).one_or_none()
        return user

    def get_links(self, user_id: int) -> list[UserLink]:
        links: list[UserLink] = (
            self._db.query(UserLink)
            .filter(
                UserLink.user_id == user_id,
            )
            .order_by(UserLink.created_at.desc())
            .all()
        )
        return links

    def get_link(self, user_id: int, link_id: int) -> UserLink | None:
        link: UserLink | None = (
            self._db.query(UserLink).filter(UserLink.user_id == user_id, UserLink.id == link_id).one_or_none()
        )
        return link

    def create_link(
        self, user_id: int, mnoneykit_link_id: str, state: str, institution_id: str, instiotution_name: str
    ) -> UserLink:
        new_link = UserLink(
            user_id=user_id,
            link_id=mnoneykit_link_id,
            state=state,
            institution_id=institution_id,
            institution_name=instiotution_name,
            transaction_sync_cursor=None,
        )
        self._db.add(new_link)
        return new_link

    def delete_link(self, link_id: int) -> None:
        self._db.execute(sqlalchemy.delete(UserLink).where(UserLink.id == link_id))
