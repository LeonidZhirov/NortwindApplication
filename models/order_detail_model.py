# models/order_detail_model.py
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order
    from models.product_model import Product


class OrderDetail(Base):
    __tablename__ = 'order_details'

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('orders.order_id'),
        primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.product_id'),
        primary_key=True
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=0
    )

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="details",
        lazy="selectin"
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="order_details",
        lazy="selectin"
    )

    @property
    def total(self) -> Decimal:
        return Decimal(str(self.unit_price * self.quantity * (1 - self.discount)))

    @property
    def discount_amount(self) -> Decimal:
        return self.unit_price * self.quantity * self.discount

    def __str__(self) -> str:
        return f"Order #{self.order_id} | {self.product.product_name} | {self.quantity} x ${float(self.unit_price):.2f} | Discount: {float(self.discount):.0%}"