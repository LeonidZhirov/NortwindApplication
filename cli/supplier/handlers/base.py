# cli/supplier/handlers/base.py
from abc import ABC
from sqlalchemy.orm import Session

from cli.common.base_handler import BaseHandler
from services import DisplayService, StockService, ProductService
from repositories import SupplierRepository


class BaseSupplierHandler(BaseHandler, ABC):
    def __init__(self, session: Session):
        super().__init__(session)
        self._display_service = DisplayService()
        self._stock_service = StockService()
        self._product_service = ProductService()
        self._supplier_repo = SupplierRepository()