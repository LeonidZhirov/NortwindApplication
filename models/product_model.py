# models/product_model.py
from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_detail_model import OrderDetail
    from models.supplier_model import Supplier
    from models.cart_item_model import CartItem
    from models.stock_alert_model import StockAlert
    from models.category_model import Category
    from models.restock_history_model import RestockHistory


class Product(Base):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    product_name: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('suppliers.supplier_id'),
        nullable=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('categories.category_id'),
        nullable=True
    )
    quantity_per_unit: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=0
    )
    units_in_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0
    )
    units_on_order: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0
    )
    reorder_level: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=0
    )
    discontinued: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
        lazy="selectin"
    )
    supplier: Mapped["Supplier"] = relationship(
        "Supplier",
        back_populates="products",
        lazy="selectin"
    )
    order_details: Mapped[List["OrderDetail"]] = relationship(
        "OrderDetail",
        back_populates="product",
        lazy="selectin"
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    stock_alerts: Mapped[List["StockAlert"]] = relationship(
        "StockAlert",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    restock_history: Mapped[List["RestockHistory"]] = relationship(
        "RestockHistory",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    @property
    def is_in_stock(self) -> bool:
        return (self.units_in_stock or 0) > 0

    @property
    def is_low_stock(self) -> bool:
        return (self.units_in_stock or 0) <= (self.reorder_level or 0)

    @property
    def needs_reorder(self) -> bool:
        return self.is_low_stock and (self.units_on_order or 0) == 0

    def can_supply(self, quantity: int) -> bool:
        return (self.units_in_stock or 0) >= quantity

    def __str__(self) -> str:
        stock_status = "⚠️" if self.is_low_stock else "✅" if self.is_in_stock else "❌"
        return f"{stock_status} {self.product_id:>3} | {self.product_name:<40} | ${float(self.unit_price or 0):>8.2f} | {(self.units_in_stock or 0):>5} шт."