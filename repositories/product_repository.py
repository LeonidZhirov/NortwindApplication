# repositories/product_repository.py
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from models.product_model import Product
from repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self):
        super().__init__(Product)

    def get_by_id(self, session: Session, product_id: int) -> Optional[Product]:
        return super().get_by_id(session, product_id)

    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Product]:
        stmt = select(Product).where(
            Product.discontinued == 0
        ).order_by(Product.product_id.asc()).limit(limit).offset(offset)  # ← asc()
        return list(session.execute(stmt).scalars().all())

    def get_all_with_discontinued(self, session: Session, limit: int = 100) -> List[Product]:
        stmt = select(Product).order_by(Product.product_id.asc()).limit(limit)
        return list(session.execute(stmt).scalars().all())

    def get_by_category(self, session: Session, category_id: int) -> List[Product]:
        stmt = select(Product).where(
            and_(Product.category_id == category_id, Product.discontinued == 0)
        ).order_by(Product.product_id.asc())  # ← asc()
        return list(session.execute(stmt).scalars().all())

    def get_by_supplier(self, session: Session, supplier_id: int) -> List[Product]:
        stmt = select(Product).where(
            and_(Product.supplier_id == supplier_id, Product.discontinued == 0)
        ).order_by(Product.product_id.asc())  # ← asc()
        return list(session.execute(stmt).scalars().all())

    def get_low_stock_products(self, session: Session) -> List[Product]:
        stmt = select(Product).where(
            and_(
                Product.discontinued == 0,
                Product.units_in_stock <= Product.reorder_level
            )
        ).order_by(Product.product_id.asc())
        return list(session.execute(stmt).scalars().all())

    def get_out_of_stock_products(self, session: Session) -> List[Product]:
        stmt = select(Product).where(
            and_(Product.discontinued == 0, Product.units_in_stock == 0)
        ).order_by(Product.product_id.asc())
        return list(session.execute(stmt).scalars().all())

    def get_with_lock(self, session: Session, product_id: int) -> Optional[Product]:
        stmt = select(Product).where(Product.product_id == product_id).with_for_update()
        return session.execute(stmt).scalar_one_or_none()

    def update_stock(self, session: Session, product_id: int, new_quantity: int) -> Optional[Product]:
        product = self.get_with_lock(session, product_id)
        if product:
            old_quantity = product.units_in_stock
            product.units_in_stock = new_quantity
            session.add(product)
            session.flush()
            print(f"🔄 update_stock: product_id={product_id}, "
                  f"было={old_quantity}, стало={new_quantity}")
            return product
        return None

    def get_stock(self, session: Session, product_id: int) -> Optional[int]:
        stmt = select(Product.units_in_stock).where(Product.product_id == product_id)
        return session.execute(stmt).scalar_one_or_none()

    def search_products(self, session: Session, query: str, limit: int = 50) -> List[Product]:
        search_term = f"%{query}%"
        stmt = select(Product).where(
            and_(
                Product.discontinued == 0,
                Product.product_name.ilike(search_term)
            )
        ).limit(limit)
        return list(session.execute(stmt).scalars().all())

    def get_products_by_price_range(self, session: Session, min_price: Decimal, max_price: Decimal) -> List[Product]:
        stmt = select(Product).where(
            and_(
                Product.discontinued == 0,
                Product.unit_price >= min_price,
                Product.unit_price <= max_price
            )
        ).order_by(Product.unit_price)
        return list(session.execute(stmt).scalars().all())

    def get_product_with_supplier(self, session: Session, product_id: int) -> Optional[Product]:
        stmt = select(Product).where(Product.product_id == product_id).options(
            joinedload(Product.supplier)
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_stock_for_product(self, session: Session, entity_id: int) -> Optional[int]:
        stmt = select(Product.units_in_stock).where(Product.product_id == entity_id)
        result = session.execute(stmt).scalar_one_or_none()
        return result or 0

