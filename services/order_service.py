from typing import List
from repositories.order_repository import OrderRepository
from models.cart_item_model import CartItem


class OrderService:
    def __init__(self, order_repository: OrderRepository):
        self.order_repo = order_repository

    def create_order(self, customer_id: str, employee_id: int,
                     cart_items: List[CartItem], ship_via: int) -> int:
        return self.order_repo.create_order(
            customer_id=customer_id,
            employee_id=employee_id,
            cart_items=cart_items,
            ship_via=ship_via
        )

    def validate_cart(self, cart_items: List[CartItem]) -> bool:
        return len(cart_items) > 0