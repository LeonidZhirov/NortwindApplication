# repositories/stock_alert_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from models.stock_alert_model import StockAlert
from repositories.base_repository import BaseRepository


class StockAlertRepository(BaseRepository[StockAlert]):
    def __init__(self):
        super().__init__(StockAlert)

    def get_by_id(self, session: Session, alert_id: int) -> Optional[StockAlert]:
        return super().get_by_id(session, alert_id)

    def get_pending_alerts(self, session: Session) -> List[StockAlert]:
        stmt = select(StockAlert).where(
            StockAlert.status == 'pending'
        ).options(
            joinedload(StockAlert.product),
            joinedload(StockAlert.supplier)
        ).order_by(StockAlert.alert_date)
        return list(session.execute(stmt).scalars().all())

    def get_alerts_by_product(self, session: Session, product_id: int) -> List[StockAlert]:
        stmt = select(StockAlert).where(
            StockAlert.product_id == product_id
        ).order_by(StockAlert.alert_date.desc())
        return list(session.execute(stmt).scalars().all())

    def get_alerts_by_supplier(self, session: Session, supplier_id: int) -> List[StockAlert]:
        stmt = select(StockAlert).where(
            and_(
                StockAlert.supplier_id == supplier_id,
                StockAlert.status == 'pending'
            )
        ).order_by(StockAlert.alert_date)
        return list(session.execute(stmt).scalars().all())

    def mark_as_resolved(self, session: Session, alert_id: int) -> Optional[StockAlert]:
        alert = self.get_by_id(session, alert_id)
        if alert:
            alert.resolve()
            session.flush()
        return alert

    def add_alert(self, session: Session, alert: StockAlert) -> StockAlert:
        session.add(alert)
        session.flush()
        return alert

    def get_alerts_by_status(self, session: Session, status: str) -> List[StockAlert]:
        stmt = select(StockAlert).where(
            StockAlert.status == status
        ).options(
            joinedload(StockAlert.product)
        ).order_by(StockAlert.alert_date)
        return list(session.execute(stmt).scalars().all())

    def get_recent_alerts(self, session: Session, days: int = 7) -> List[StockAlert]:
        from datetime import date, timedelta
        since_date = date.today() - timedelta(days=days)
        stmt = select(StockAlert).where(
            StockAlert.alert_date >= since_date
        ).order_by(StockAlert.alert_date.desc())
        return list(session.execute(stmt).scalars().all())