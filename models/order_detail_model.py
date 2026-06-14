from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order

class OrderDetail(Base):
    __tablename__ = 'order_details'

    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0.0)

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="details",
        lazy="selectin"
    )


    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity * (1 - Decimal(str(self.discount)))