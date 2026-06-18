# repositories/cart_repository.py
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_, delete
from models.cart_item_model import CartItem
from repositories.base_repository import BaseRepository


class CartRepository(BaseRepository[CartItem]):
    def __init__(self):
        super().__init__(CartItem)

    def get_by_id(self, session: Session, cart_item_id: int) -> Optional[CartItem]:
        return super().get_by_id(session, cart_item_id)

    def get_cart_by_customer(self, session: Session, customer_id: str) -> List[CartItem]:
        stmt = select(CartItem).where(
            CartItem.customer_id == customer_id
        ).options(
            joinedload(CartItem.product)
        )
        return list(session.execute(stmt).scalars().all())

    def add_to_cart(
            self,
            session: Session,
            customer_id: str,
            product_id: int,
            quantity: int,
            unit_price: Decimal,
            product_name: str
    ) -> CartItem:
        stmt = select(CartItem).where(
            and_(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            )
        )
        existing = session.execute(stmt).scalar_one_or_none()

        if existing:
            existing.quantity += quantity
            session.flush()
            return existing
        else:
            cart_item = CartItem(
                customer_id=customer_id,
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price
            )
            session.add(cart_item)
            session.flush()
            return cart_item

    def remove_from_cart(self, session: Session, customer_id: str, product_id: int) -> bool:
        stmt = delete(CartItem).where(
            and_(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            )
        )
        result = session.execute(stmt)
        session.flush()
        return result.rowcount > 0

    def update_quantity(
            self,
            session: Session,
            customer_id: str,
            product_id: int,
            quantity: int
    ) -> Optional[CartItem]:
        stmt = select(CartItem).where(
            and_(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            )
        )
        cart_item = session.execute(stmt).scalar_one_or_none()

        if not cart_item:
            return None

        if quantity <= 0:
            self.remove_from_cart(session, customer_id, product_id)
            return None

        cart_item.quantity = quantity
        session.flush()
        return cart_item

    def clear_cart(self, session: Session, customer_id: str) -> int:
        stmt = delete(CartItem).where(CartItem.customer_id == customer_id)
        result = session.execute(stmt)
        session.flush()
        return result.rowcount

    def get_cart_total(self, session: Session, customer_id: str) -> Decimal:
        cart_items = self.get_cart_by_customer(session, customer_id)
        total = Decimal('0')
        for item in cart_items:
            total += item.quantity * item.unit_price
        return total

    def get_cart_items_count(self, session: Session, customer_id: str) -> int:
        stmt = select(func.count()).where(CartItem.customer_id == customer_id)
        return session.execute(stmt).scalar() or 0

    def get_by_customer_and_product(
            self,
            session: Session,
            customer_id: str,
            product_id: int
    ) -> Optional[CartItem]:
        stmt = select(CartItem).where(
            and_(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    def delete(self, session: Session, cart_item_id: int) -> bool:
        cart_item = self.get_by_id(session, cart_item_id)
        if cart_item:
            session.delete(cart_item)
            session.flush()
            return True
        return False

    def delete_by_customer_and_product(
            self,
            session: Session,
            customer_id: str,
            product_id: int
    ) -> bool:
        cart_item = self.get_by_customer_and_product(session, customer_id, product_id)
        if cart_item:
            session.delete(cart_item)
            session.flush()
            return True
        return False