from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order


class Customer(Base):
    __tablename__ = 'customers'

    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(40), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(30), nullable=False)

    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="customer",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return f"{self.customer_id:<10} | {self.company_name:<40} | {self.contact_name:<30}"