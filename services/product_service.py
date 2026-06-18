# services/product_service.py
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from repositories import ProductRepository, SupplierRepository
from models import Product


class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.supplier_repo = SupplierRepository()

    def get_all_products(self, session: Session, limit: int = 100, offset: int = 0) -> List[Product]:
        return self.product_repo.get_all(session, limit, offset)

    def get_product(self, session: Session, product_id: int) -> Optional[Product]:
        return self.product_repo.get_by_id(session, product_id)

    def get_product_with_supplier(self, session: Session, product_id: int) -> Optional[Product]:
        return self.product_repo.get_product_with_supplier(session, product_id)

    def get_products_by_category(self, session: Session, category_id: int) -> List[Product]:
        return self.product_repo.get_by_category(session, category_id)

    def get_products_by_supplier(self, session: Session, supplier_id: int) -> List[Product]:
        return self.product_repo.get_by_supplier(session, supplier_id)

    def get_products_by_price_range(
        self,
        session: Session,
        min_price: Decimal,
        max_price: Decimal
    ) -> List[Product]:
        return self.product_repo.get_products_by_price_range(session, min_price, max_price)

    def get_low_stock_products(self, session: Session) -> List[Product]:
        return self.product_repo.get_low_stock_products(session)

    def get_out_of_stock_products(self, session: Session) -> List[Product]:
        return self.product_repo.get_out_of_stock_products(session)

    def search_products(self, session: Session, query: str, limit: int = 50) -> List[Product]:
        return self.product_repo.search_products(session, query, limit)

    def get_stock_info(self, session: Session, product_id: int) -> Optional[Dict[str, Any]]:
        product = self.get_product(session, product_id)
        if not product:
            return None

        return {
            'product_id': product.product_id,
            'product_name': product.product_name,
            'units_in_stock': product.units_in_stock or 0,
            'reorder_level': product.reorder_level or 0,
            'is_low_stock': product.is_low_stock,
            'is_in_stock': product.is_in_stock,
            'is_discontinued': product.discontinued == 1
        }

    def check_availability(self, session: Session, product_id: int, quantity: int) -> tuple[bool, str, Optional[int]]:
        product = self.get_product(session, product_id)
        if not product:
            return False, "Товар не найден", None

        if product.discontinued:
            return False, "Товар снят с производства", None

        available = product.units_in_stock or 0
        if available <= 0:
            return False, "Товар временно отсутствует на складе", 0

        if available >= quantity:
            return True, "Достаточно товара", available

        return False, f"Недостаточно товара. Доступно: {available} шт.", available

    def get_product_info(self, session: Session, product_id: int) -> Optional[Dict[str, Any]]:
        product = self.get_product_with_supplier(session, product_id)
        if not product:
            return None

        return {
            'id': product.product_id,
            'name': product.product_name,
            'unit_price': product.unit_price,
            'units_in_stock': product.units_in_stock or 0,
            'reorder_level': product.reorder_level or 0,
            'discontinued': product.discontinued == 1,
            'category_id': product.category_id,
            'supplier': product.supplier.company_name if product.supplier else None,
            'supplier_id': product.supplier_id,
            'is_low_stock': product.is_low_stock,
            'is_in_stock': product.is_in_stock,
            'quantity_per_unit': product.quantity_per_unit
        }

    def get_products_summary(self, session: Session, limit: int = 100) -> List[Dict[str, Any]]:
        products = self.get_all_products(session, limit)
        return [
            {
                'id': p.product_id,
                'name': p.product_name,
                'price': p.unit_price,
                'stock': p.units_in_stock or 0,
                'status': '⚠️ Низкий остаток' if p.is_low_stock else '✅ В наличии' if p.is_in_stock else '❌ Нет в наличии'
            }
            for p in products
        ]