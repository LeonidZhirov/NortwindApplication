# repositories/customer_repository.py
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from models.customer_model import Customer
from models.order_model import Order
from repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self):
        super().__init__(Customer)

    def get_by_id(self, session: Session, customer_id: str) -> Optional[Customer]:
        return super().get_by_id(session, customer_id)

    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Customer]:
        stmt = select(Customer).order_by(Customer.company_name).limit(limit).offset(offset)
        return list(session.execute(stmt).scalars().all())

    def search(self, session: Session, query: str, limit: int = 50) -> List[Customer]:
        search_term = f"%{query}%"
        stmt = select(Customer).where(
            or_(
                Customer.company_name.ilike(search_term),
                Customer.contact_name.ilike(search_term),
                Customer.customer_id.ilike(search_term)
            )
        ).limit(limit)
        return list(session.execute(stmt).scalars().all())

    def get_customers_with_orders(self, session: Session, min_orders: int = 1) -> List[Customer]:
        stmt = select(Customer).join(Customer.orders).group_by(Customer.customer_id).having(
            func.count(Order.order_id) >= min_orders
        ).order_by(Customer.company_name)
        return list(session.execute(stmt).scalars().all())

    def get_customers_by_country(self, session: Session, country: str) -> List[Customer]:
        stmt = select(Customer).where(
            Customer.country == country
        ).order_by(Customer.company_name)
        return list(session.execute(stmt).scalars().all())

    def get_top_customers_by_order_count(self, session: Session, limit: int = 10) -> List[Tuple[Customer, int]]:
        stmt = select(
            Customer,
            func.count(Order.order_id).label('order_count')
        ).join(Customer.orders).group_by(Customer.customer_id).order_by(
            func.count(Order.order_id).desc()
        ).limit(limit)

        result = session.execute(stmt).all()
        return [(row[0], row[1]) for row in result]

    def get_top_customers_by_total(self, session: Session, limit: int = 10) -> List[Tuple[Customer, float]]:
        stmt = select(
            Customer,
            func.sum(Order.total_amount).label('total_amount')
        ).join(Customer.orders).where(
            Order.shipped_date.is_not(None)
        ).group_by(Customer.customer_id).order_by(
            func.sum(Order.total_amount).desc()
        ).limit(limit)

        result = session.execute(stmt).all()
        return [(row[0], float(row[1]) if row[1] else 0.0) for row in result]