from typing import TYPE_CHECKING
from datetime import date
from sqlalchemy import Integer, ForeignKey, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.product_model import Product
    from models.supplier_model import Supplier


class StockAlert(Base):
    __tablename__ = 'stock_alerts'

    alert_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.product_id'),
        nullable=False,
        index=True
    )
    current_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    reorder_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    alert_date: Mapped[date] = mapped_column(
        Date,
        default=date.today
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default='pending'
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('suppliers.supplier_id'),
        nullable=False
    )
    resolved_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )
    notes: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="stock_alerts",
        lazy="selectin"
    )
    supplier: Mapped["Supplier"] = relationship(
        "Supplier",
        back_populates="stock_alerts",
        lazy="selectin"
    )

    @property
    def is_resolved(self) -> bool:
        return self.status == 'resolved'

    @property
    def is_pending(self) -> bool:
        return self.status == 'pending'

    def resolve(self):
        self.status = 'resolved'
        self.resolved_date = date.today()

    def __str__(self) -> str:
        status_icon = "✅" if self.is_resolved else "⚠️"
        return f"{status_icon} Alert #{self.alert_id} | {self.product.product_name} | Stock: {self.current_stock} | Reorder: {self.reorder_level}"