from contextlib import contextmanager
from typing import Generator, Callable
from sqlalchemy.orm import Session
from cli.io_utils import T

from db import get_session


class SessionManager:
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        with get_session() as session:
            yield session

    def execute_in_transaction(self, func: Callable[[Session], T]) -> T:
        with get_session() as session:
            try:
                result = func(session)
                session.commit()
                return result
            except Exception:
                session.rollback()
                raise