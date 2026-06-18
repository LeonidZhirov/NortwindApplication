from abc import ABC
from typing import Optional
from sqlalchemy.orm import Session

from cli.io_utils import get_valid_int, get_confirmation, wait_for_key, display_header


class BaseHandler(ABC):
    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def _display_header(self, title: str) -> None:
        display_header(title)

    def _wait(self) -> None:
        wait_for_key()

    def _confirm(self, prompt: str = "Подтвердить? (y/n): ") -> bool:
        return get_confirmation(prompt)

    def _input_int(self, prompt: str, **kwargs) -> Optional[int]:
        return get_valid_int(prompt, **kwargs)

    def _input_choice(self, prompt: str, max_value: int) -> Optional[int]:
        return get_valid_int(
            prompt,
            validator=lambda x: 0 <= x <= max_value
        )