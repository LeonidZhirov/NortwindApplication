# models/restock_history_model.py
from datetime import date
from sqlalchemy import Integer, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Base, Product, Supplier



class RestockHistory(Base):
    __tablename__ = 'restock_history'

    restock_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.product_id'), nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey('suppliers.supplier_id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    new_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    restock_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="restock_history")
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="restock_history")