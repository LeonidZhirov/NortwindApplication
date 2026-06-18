# repositories/restock_history_repository.py
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from models.restock_history_model import RestockHistory
from repositories.base_repository import BaseRepository


class RestockHistoryRepository(BaseRepository[RestockHistory]):
    def __init__(self):
        super().__init__(RestockHistory)

    def get_by_supplier(
            self,
            session: Session,
            supplier_id: int,
            limit: int = 50,
            offset: int = 0
    ) -> List[RestockHistory]:
        stmt = select(self.model).where(
            RestockHistory.supplier_id == supplier_id
        ).order_by(
            RestockHistory.restock_date.desc()
        ).limit(limit).offset(offset)
        return list(session.execute(stmt).scalars().all())

    def get_by_product(
            self,
            session: Session,
            product_id: int,
            limit: int = 20
    ) -> List[RestockHistory]:
        stmt = select(self.model).where(
            RestockHistory.product_id == product_id
        ).order_by(
            RestockHistory.restock_date.desc()
        ).limit(limit)
        return list(session.execute(stmt).scalars().all())

    def get_by_date_range(
            self,
            session: Session,
            supplier_id: int,
            start_date: date,
            end_date: date,
            limit: int = 100
    ) -> List[RestockHistory]:
        stmt = select(self.model).where(
            and_(
                RestockHistory.supplier_id == supplier_id,
                RestockHistory.restock_date >= start_date,
                RestockHistory.restock_date <= end_date
            )
        ).order_by(
            RestockHistory.restock_date.desc()
        ).limit(limit)
        return list(session.execute(stmt).scalars().all())

    def get_stats_by_supplier(
            self,
            session: Session,
            supplier_id: int
    ) -> dict:
        from sqlalchemy import func

        stmt = select(
            func.count(RestockHistory.restock_id).label('total_restocks'),
            func.sum(RestockHistory.quantity).label('total_quantity'),
            func.avg(RestockHistory.quantity).label('avg_quantity')
        ).where(RestockHistory.supplier_id == supplier_id)

        result = session.execute(stmt).first()
        return {
            'total_restocks': result.total_restocks or 0,
            'total_quantity': result.total_quantity or 0,
            'avg_quantity': float(result.avg_quantity or 0)
        }