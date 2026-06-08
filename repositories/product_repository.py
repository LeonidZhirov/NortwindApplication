from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from models.product_model import Product


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Product]:
        return list(self.session.execute(
            select(Product)
            .where(Product.discontinued == 0)
            .order_by(Product.product_name)
        ).scalars().all())

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.execute(
            select(Product)
            .where(
                and_(
                    Product.product_id == product_id,
                    Product.discontinued == 0
                )
            )
        ).scalar_one_or_none()

    def check_stock(self, product_id: int, required_quantity: int) -> bool:
        product = self.session.get(Product, product_id)
        if not product:
            return False
        return bool(product.units_in_stock >= required_quantity)