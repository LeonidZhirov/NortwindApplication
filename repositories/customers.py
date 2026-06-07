from sqlalchemy import text
from typing import List, Optional
from db import get_connection
from models.customer_model import Customer

class CustomerRepository:
    @staticmethod
    def get_all() -> List[Customer]:
        with get_connection() as conn:
            result = conn.execute(text("""
                SELECT customer_id, company_name, contact_name 
                FROM customers 
                ORDER BY company_name
            """))
            return [
                Customer(
                    customer_id=row[0],
                    company_name=row[1],
                    contact_name=row[2]
                )
                for row in result.fetchall()
            ]

    @staticmethod
    def get_by_id(customer_id: str) -> Optional[Customer]:
        with get_connection() as conn:
            result = conn.execute(
                text("SELECT customer_id, company_name, contact_name FROM customers WHERE customer_id = :cid"),
                {"cid": customer_id}
            )
            row = result.first()
            if row:
                return Customer(
                    customer_id=row[0],
                    company_name=row[1],
                    contact_name=row[2]
                )
            return None