# cli/executor/handlers/base.py
from abc import ABC
from sqlalchemy.orm import Session

from cli.common.base_handler import BaseHandler
from services import OrderService, StockService, DisplayService


class BaseExecutorHandler(BaseHandler, ABC):
    def __init__(self, session: Session):
        super().__init__(session)
        self._order_service = OrderService()
        self._stock_service = StockService()
        self._display_service = DisplayService()