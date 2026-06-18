from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order


class Shipper(Base):
    __tablename__ = 'shippers'

    shipper_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    company_name: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )
    phone: Mapped[str] = mapped_column(
        String(24),
        nullable=True
    )

    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="shipper",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return f"{self.shipper_id}. {self.company_name} | {self.phone or 'N/A'}"