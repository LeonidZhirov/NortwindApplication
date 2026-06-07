from sqlalchemy import text
from typing import List, Optional
from decimal import Decimal
from db import get_connection
from models.product_model import Product


class ProductRepository:
    @staticmethod
    def get_all() -> List[Product]:
        with get_connection() as conn:
            result = conn.execute(text("""
                SELECT product_id, product_name, unit_price, units_in_stock, reorder_level, discontinued
                FROM products 
                WHERE discontinued = 0
                ORDER BY product_name
            """))
            return [
                Product(
                    product_id=row[0],
                    product_name=row[1],
                    unit_price=Decimal(str(row[2])),
                    units_in_stock=row[3],
                    reorder_level=row[4],
                    discontinued=row[5]
                )
                for row in result.fetchall()
            ]

    @staticmethod
    def get_by_id(product_id: int) -> Optional[Product]:
        with get_connection() as conn:
            result = conn.execute(
                text("""
                    SELECT product_id, product_name, unit_price, units_in_stock, reorder_level, discontinued
                    FROM products 
                    WHERE product_id = :pid AND discontinued = 0
                """),
                {"pid": product_id}
            )
            row = result.first()
            if row:
                return Product(
                    product_id=row[0],
                    product_name=row[1],
                    unit_price=Decimal(str(row[2])),
                    units_in_stock=row[3],
                    reorder_level=row[4],
                    discontinued=row[5]
                )
            return None

    @staticmethod
    def check_stock(product_id: int, required_quantity: int) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                text("SELECT units_in_stock FROM products WHERE product_id = :pid"),
                {"pid": product_id}
            )
            stock = result.scalar()
            return stock >= required_quantity