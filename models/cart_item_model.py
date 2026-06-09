from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order


class CartItem(Base):
    __tablename__ = 'cart_items'

    cart_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    orders: Mapped[List["Order"]] = relationship(
        "Order",
        secondary="order_cart_items",
        back_populates="cart_items",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return f"{self.product_name} x{self.quantity} = {self.total}"

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity