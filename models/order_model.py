from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_detail_model import OrderDetail
    from models.cart_item_model import CartItem
    from models.customer_model import Customer


class Order(Base):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    customer_id: Mapped[
        str] = mapped_column(String(10), ForeignKey('customers.customer_id'), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey('employees.employee_id'), nullable=False)
    ship_via: Mapped[int] = mapped_column(Integer, ForeignKey('shippers.shipper_id'), nullable=False)

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="orders",
        lazy="selectin"
    )

    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        secondary="order_cart_items",
        lazy="selectin",
        back_populates="orders"
    )

    details: Mapped[List["OrderDetail"]] = relationship(
        "OrderDetail",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return f"Order #{self.order_id} | {self.customer_id}"