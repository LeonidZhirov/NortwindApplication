# repositories/order_repository.py
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, and_, func
from models.order_model import Order
from models.order_detail_model import OrderDetail
from repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self):
        super().__init__(Order)

    def get_by_id(self, session: Session, order_id: int) -> Optional[Order]:
        stmt = select(Order).where(Order.order_id == order_id).options(
            joinedload(Order.customer),
            joinedload(Order.employee),
            joinedload(Order.shipper),
            joinedload(Order.details).joinedload(OrderDetail.product)
        )
        return session.execute(stmt).unique().scalar_one_or_none()

    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Order]:
        stmt = select(Order).order_by(Order.order_date.desc()).limit(limit).offset(offset)
        return list(session.execute(stmt).unique().scalars().all())

    def create_order(self, session: Session, order: Order) -> Order:
        session.add(order)
        session.flush()
        return order

    def get_unshipped_orders(self, session: Session) -> List[Order]:
        stmt = select(Order).where(Order.shipped_date.is_(None)).options(
            joinedload(Order.customer),
            joinedload(Order.details)
        ).order_by(Order.order_date)
        return list(session.execute(stmt).unique().scalars().all())

    def get_shipped_orders(self, session: Session, limit: int = 50) -> List[Order]:
        stmt = select(Order).where(Order.shipped_date.is_not(None)).options(
            joinedload(Order.customer)
        ).order_by(Order.shipped_date.desc()).limit(limit)
        return list(session.execute(stmt).unique().scalars().all())

    def update_shipped_date(self, session: Session, order_id: int, shipped_date: date) -> Optional[Order]:
        return self.update(session, order_id, shipped_date=shipped_date)

    def get_orders_by_customer(self, session: Session, customer_id: str) -> List[Order]:
        stmt = select(Order).where(Order.customer_id == customer_id).options(
            joinedload(Order.details)
        ).order_by(Order.order_date.desc())
        return list(session.execute(stmt).unique().scalars().all())

    def get_orders_by_date_range(
            self,
            session: Session,
            start_date: date,
            end_date: date
    ) -> List[Order]:
        stmt = select(Order).where(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            )
        ).order_by(Order.order_date)
        return list(session.execute(stmt).unique().scalars().all())

    def get_orders_by_employee(self, session: Session, employee_id: int) -> List[Order]:
        stmt = select(Order).where(Order.employee_id == employee_id).order_by(
            Order.order_date.desc()
        )
        return list(session.execute(stmt).unique().scalars().all())

    def get_recent_orders(self, session: Session, days: int = 7) -> List[Order]:
        since_date = date.today() - timedelta(days=days)
        return self.get_orders_by_date_range(session, since_date, date.today())

    def get_total_orders_count(self, session: Session) -> int:
        return self.count(session)

    def get_shipped_orders_count(self, session: Session) -> int:
        stmt = select(func.count()).where(Order.shipped_date.is_not(None))
        return session.execute(stmt).unique().scalar() or 0

    def get_unshipped_orders_count(self, session: Session) -> int:
        stmt = select(func.count()).where(Order.shipped_date.is_(None))
        return session.execute(stmt).unique().scalar() or 0

    def get_total_amount_sum(self, session: Session) -> Decimal:
        stmt = select(func.sum(OrderDetail.unit_price * OrderDetail.quantity))
        result = session.execute(stmt).scalar()
        return Decimal(str(result or 0))

    def get_average_order_amount(self, session: Session) -> Decimal:
        total = self.get_total_amount_sum(session)
        count = self.get_total_orders_count(session)
        if count == 0:
            return Decimal('0')
        return total / count

    def get_order_with_details(self, session: Session, order_id: int) -> Optional[Order]:
        stmt = select(Order).where(Order.order_id == order_id).options(
            joinedload(Order.customer),
            joinedload(Order.employee),
            joinedload(Order.shipper),
            joinedload(Order.details).joinedload(OrderDetail.product)  # ← Загружаем всё
        )
        return session.execute(stmt).unique().scalar_one_or_none()

    def get_order_for_shipping(self, session: Session, order_id: int) -> Optional[Order]:
        stmt = select(Order).where(Order.order_id == order_id).options(
            selectinload(Order.details).selectinload(OrderDetail.product)
        ).with_for_update()
        return session.execute(stmt).unique().scalar_one_or_none()