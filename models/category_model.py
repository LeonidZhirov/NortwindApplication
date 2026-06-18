# models/category_model.py
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.product_model import Product


class Category(Base):
    __tablename__ = 'categories'

    category_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    category_name: Mapped[str] = mapped_column(
        String(15),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    picture: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=True
    )


    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return f"{self.category_id:>3} | {self.category_name:<15} | {self.description[:50] if self.description else 'N/A'}"