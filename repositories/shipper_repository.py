# repositories/shipper_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.shipper_model import Shipper
from repositories.base_repository import BaseRepository


class ShipperRepository(BaseRepository[Shipper]):
    def __init__(self):
        super().__init__(Shipper)

    def get_by_id(self, session: Session, shipper_id: int) -> Optional[Shipper]:
        return super().get_by_id(session, shipper_id)

    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Shipper]:
        stmt = select(Shipper).order_by(Shipper.shipper_id.asc()).limit(limit).offset(offset)
        return list(session.execute(stmt).scalars().all())

    def get_default_shipper(self, session: Session) -> Optional[Shipper]:
        stmt = select(Shipper).order_by(Shipper.shipper_id.asc()).limit(1)
        return session.execute(stmt).scalar_one_or_none()

    def get_by_company_name(self, session: Session, company_name: str) -> Optional[Shipper]:
        stmt = select(Shipper).where(Shipper.company_name == company_name)
        return session.execute(stmt).scalar_one_or_none()

    def search_by_name(self, session: Session, query: str, limit: int = 50) -> List[Shipper]:
        search_term = f"%{query}%"
        stmt = select(Shipper).where(
            Shipper.company_name.ilike(search_term)
        ).limit(limit)
        return list(session.execute(stmt).scalars().all())