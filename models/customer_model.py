from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order
    from models.cart_item_model import CartItem


class Customer(Base):
    __tablename__ = 'customers'

    customer_id: Mapped[str] = mapped_column(
        String(5),
        primary_key=True
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

    # Relationships
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="customer",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="customer",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    @property
    def total_orders_amount(self) -> float:
        return sum(order.total_amount for order in self.orders if order.is_shipped)

    @property
    def orders_count(self) -> int:
        return len(self.orders)

    def __str__(self) -> str:
        return f"{self.customer_id:<10} | {self.company_name:<40} | {self.contact_name or 'N/A':<30}"