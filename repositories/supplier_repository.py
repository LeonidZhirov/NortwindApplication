# repositories/supplier_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, or_
from models.supplier_model import Supplier
from repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self):
        super().__init__(Supplier)

    def get_by_id(self, session: Session, supplier_id: int) -> Optional[Supplier]:
        return super().get_by_id(session, supplier_id)

    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Supplier]:
        stmt = select(Supplier).order_by(Supplier.supplier_id.asc()).limit(limit).offset(offset)  # ← asc()
        return list(session.execute(stmt).scalars().all())

    def get_suppliers_with_products(self, session: Session) -> List[Supplier]:
        stmt = select(Supplier).where(
            Supplier.products.any()
        ).order_by(Supplier.company_name)
        return list(session.execute(stmt).scalars().all())

    def get_suppliers_by_country(self, session: Session, country: str) -> List[Supplier]:
        stmt = select(Supplier).where(
            Supplier.country == country
        ).order_by(Supplier.company_name)
        return list(session.execute(stmt).scalars().all())

    def search_suppliers(self, session: Session, query: str, limit: int = 50) -> List[Supplier]:
        search_term = f"%{query}%"
        stmt = select(Supplier).where(
            or_(
                Supplier.company_name.ilike(search_term),
                Supplier.contact_name.ilike(search_term)
            )
        ).limit(limit)
        return list(session.execute(stmt).scalars().all())

    def get_supplier_with_products(self, session: Session, supplier_id: int) -> Optional[Supplier]:
        stmt = select(Supplier).where(
            Supplier.supplier_id == supplier_id
        ).options(
            joinedload(Supplier.products)
        )
        return session.execute(stmt).scalar_one_or_none()