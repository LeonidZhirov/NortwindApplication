from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order
    from models.product_model import Product
    from models.customer_model import Customer


class CartItem(Base):
    __tablename__ = 'cart_items'

    cart_item_id: Mapped[int] = mapped_column(
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
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.product_id'),
        nullable=False,
        index=True
    )
    product_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="cart_items",
        lazy="selectin"
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="cart_items",
        lazy="selectin"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        secondary="order_cart_items",
        back_populates="cart_items",
        lazy="selectin"
    )

    @property
    def total(self) -> Decimal:
        return Decimal(str(self.unit_price * self.quantity))

    def __str__(self) -> str:
        return f"CartItem: {self.product.product_name} x{self.quantity} = ${float(self.total):.2f}"