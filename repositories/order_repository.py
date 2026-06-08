from typing import List
from sqlalchemy.orm import Session
from models.cart_item_model import CartItem
from models.order_model import Order
from models.order_detail_model import OrderDetail


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_order(self, customer_id: str, employee_id: int,
                     cart_items: List[CartItem], ship_via: int = 1) -> int:

        order = Order(
            customer_id=customer_id,
            employee_id=employee_id,
            ship_via=ship_via
        )

        self.session.add(order)

        for item in cart_items:
            order_detail = OrderDetail(
                order=order,
                product_id=item.product_id,
                unit_price=item.unit_price,
                quantity=item.quantity,
                discount=0.0
            )
            self.session.add(order_detail)

        self.session.flush()

        return order.id