from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.product_model import Product
    from models.stock_alert_model import StockAlert
    from models.restock_history_model import RestockHistory


class Supplier(Base):
    __tablename__ = 'suppliers'

    supplier_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    company_name: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )
    contact_name: Mapped[str] = mapped_column(
        String(30),
        nullable=True
    )
    contact_title: Mapped[str] = mapped_column(
        String(30),
        nullable=True
    )
    address: Mapped[str] = mapped_column(
        String(60),
        nullable=True
    )
    city: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    region: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    postal_code: Mapped[str] = mapped_column(
        String(10),
        nullable=True
    )
    country: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    phone: Mapped[str] = mapped_column(
        String(24),
        nullable=True
    )
    fax: Mapped[str] = mapped_column(
        String(24),
        nullable=True
    )
    homepage: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="supplier",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    stock_alerts: Mapped[List["StockAlert"]] = relationship(
        "StockAlert",
        back_populates="supplier",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    restock_history: Mapped[List["RestockHistory"]] = relationship(
        "RestockHistory",
        back_populates="supplier",
        cascade="all, delete-orphan"
    )

    @property
    def products_count(self) -> int:
        return len(self.products)

    @property
    def active_products(self) -> List["Product"]:
        return [p for p in self.products if not p.discontinued]

    def __str__(self) -> str:
        return f"{self.supplier_id:>3} | {self.company_name:<40} | {self.contact_name or 'N/A':<30} | {self.country or 'N/A'}"