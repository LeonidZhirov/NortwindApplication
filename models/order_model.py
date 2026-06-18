from typing import List, TYPE_CHECKING
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Date, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_detail_model import OrderDetail
    from models.customer_model import Customer
    from models.employee_model import Employee
    from models.shipper_model import Shipper
    from models.cart_item_model import CartItem


class Order(Base):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    customer_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey('customers.customer_id'),
        nullable=False,
        index=True
    )
    employee_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('employees.employee_id'),
        nullable=False
    )
    order_date: Mapped[date] = mapped_column(
        Date,
        nullable=True,
        default=date.today
    )
    required_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )
    shipped_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )
    ship_via: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('shippers.shipper_id'),
        nullable=True
    )
    freight: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=0
    )
    ship_name: Mapped[str] = mapped_column(
        String(40),
        nullable=True
    )
    ship_address: Mapped[str] = mapped_column(
        String(60),
        nullable=True
    )
    ship_city: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    ship_region: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    ship_postal_code: Mapped[str] = mapped_column(
        String(10),
        nullable=True
    )
    ship_country: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="orders",
        lazy="selectin"
    )
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="orders",
        lazy="selectin"
    )
    shipper: Mapped["Shipper"] = relationship(
        "Shipper",
        back_populates="orders",
        lazy="selectin"
    )
    details: Mapped[List["OrderDetail"]] = relationship(
        "OrderDetail",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        secondary="order_cart_items",
        back_populates="orders",
        lazy="selectin"
    )

    @property
    def is_shipped(self) -> bool:
        return self.shipped_date is not None

    @property
    def total_amount(self) -> Decimal:
        return Decimal(sum(detail.total for detail in self.details))

    @property
    def items_count(self) -> int:
        return len(self.details)

    @property
    def total_quantity(self) -> int:
        return sum(detail.quantity for detail in self.details)

    @staticmethod
    def generate_next_id(session) -> int:
        max_id = session.query(func.max(Order.order_id)).scalar()
        return (max_id or 0) + 1

    def __str__(self) -> str:
        status = "✅" if self.is_shipped else "⏳"
        return f"{status} #{self.order_id} | {self.order_date} | {self.customer.company_name[:30] if self.customer else 'N/A'} | ${float(self.total_amount):.2f}"