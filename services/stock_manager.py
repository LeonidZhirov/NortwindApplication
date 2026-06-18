# services/stock_manager.py
from typing import List, Dict, Tuple, Optional, Any
from sqlalchemy.orm import Session
from repositories.product_repository import ProductRepository
from models.product_model import Product
import logging

logger = logging.getLogger(__name__)


class InsufficientStockError(Exception):
    def __init__(self, product_id: int, product_name: str, required: int, available: int):
        self.product_id = product_id
        self.product_name = product_name
        self.required = required
        self.available = available
        super().__init__(
            f"Недостаточно товара '{product_name}' на складе. "
            f"Доступно: {available}, требуется: {required}"
        )


class StockManager:
    def __init__(self):
        self.product_repo = ProductRepository()

    def reserve(self, session: Session, product_id: int, quantity: int) -> Product:
        if quantity <= 0:
            raise ValueError("Количество должно быть > 0")

        product = self.product_repo.get_with_lock(session, product_id)
        if not product:
            raise ValueError(f"Товар #{product_id} не найден")

        current_stock = product.units_in_stock or 0
        if current_stock < quantity:
            raise InsufficientStockError(
                product_id=product_id,
                product_name=product.product_name,
                required=quantity,
                available=current_stock
            )


        new_stock = current_stock - quantity

        logger.info(f"Резервируем: product_id={product_id}, "
                    f"было={current_stock}, стало={new_stock}, "
                    f"списано={quantity}")

        product.units_in_stock = new_stock

        session.add(product)
        session.flush()

        return product

    def release(self, session: Session, product_id: int, quantity: int) -> Product:
        if quantity <= 0:
            raise ValueError("Количество должно быть > 0")

        product = self.product_repo.get_with_lock(session, product_id)
        if not product:
            raise ValueError(f"Товар #{product_id} не найден")

        current_stock = product.units_in_stock or 0
        new_stock = current_stock + quantity
        return self.product_repo.update_stock(session, product_id, new_stock)

    def reserve_multiple(
        self,
        session: Session,
        items: List[Dict[str, int]]
    ) -> List[Tuple[Product, int]]:
        result = []
        for item in items:
            product = self.reserve(session, item['product_id'], item['quantity'])
            result.append((product, item['quantity']))
        return result

    def release_multiple(
        self,
        session: Session,
        items: List[Dict[str, int]]
    ) -> List[Tuple[Product, int]]:
        result = []
        for item in items:
            product = self.release(session, item['product_id'], item['quantity'])
            result.append((product, item['quantity']))
        return result

    def check_availability(
        self,
        session: Session,
        product_id: int,
        quantity: int
    ) -> Tuple[bool, str, Optional[int]]:
        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return False, "Товар не найден", None

        if product.discontinued:
            return False, "Товар снят с производства", None

        available = product.units_in_stock or 0
        if available >= quantity:
            return True, "Достаточно товара", available
        else:
            return False, f"Недостаточно. Доступно: {available}", available

    def get_stock_info(self, session: Session, product_id: int) -> Dict[str, Any]:
        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return {'available': 0, 'is_low': True, 'is_in_stock': False}

        return {
            'available': product.units_in_stock or 0,
            'reorder_level': product.reorder_level or 0,
            'is_low': product.is_low_stock,
            'is_in_stock': product.is_in_stock
        }