from typing import List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from models.cart_item_model import CartItem


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[
        str] = mapped_column(String(10), ForeignKey('customers.customer_id'), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey('employees.employee_id'), nullable=False)
    ship_via: Mapped[int] = mapped_column(Integer, ForeignKey('shippers.shipper_id'), nullable=False)

    items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        secondary="order_cart_items",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return f"Order #{self.id} | {self.customer_id}"