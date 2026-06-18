# services/cart_service.py
from typing import List, Optional, Dict, Any, NamedTuple
from decimal import Decimal
from sqlalchemy.orm import Session

from repositories import CartRepository, ProductRepository
from models import CartItem, Product

class AddProductResult(NamedTuple):
    success: bool
    message: str
    cart_item: Optional[CartItem]


class UpdateQuantityResult(NamedTuple):
    success: bool
    message: str
    cart_item: Optional[CartItem]


class CartService:
    def __init__(self):
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()

    def get_cart(self, session: Session, customer_id: str) -> List[CartItem]:
        return self.cart_repo.get_cart_by_customer(session, customer_id)

    def _validate_product_exists(self, session: Session, product_id: int) -> Optional[Product]:
        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return None
        if product.discontinued:
            return None
        return product

    def _check_stock_availability(
            self,
            session: Session,
            product_id: int,
            customer_id: str,
            quantity: int
    ) -> tuple[bool, str, Optional[int]]:
        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return False, "Товар не найден", None

        if product.discontinued:
            return False, "Товар снят с производства", None

        current_cart = self.cart_repo.get_cart_by_customer(session, customer_id)
        current_item = next(
            (item for item in current_cart if item.product_id == product_id),
            None
        )
        current_qty = current_item.quantity if current_item else 0
        available_stock = (product.units_in_stock or 0) - current_qty

        if available_stock <= 0:
            return False, "Товар временно недоступен", 0

        if quantity > available_stock:
            return False, f"Недостаточно товара. Можно добавить максимум {available_stock} шт.", available_stock

        return True, "Достаточно товара", available_stock

    def add_product(
            self,
            session: Session,
            customer_id: str,
            product_id: int,
            quantity: int
    ) -> AddProductResult:
        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return AddProductResult(False, "Товар не найден", None)

        if product.discontinued:
            return AddProductResult(False, "Товар снят с производства", None)

        available = product.units_in_stock or 0
        if available < quantity:
            return AddProductResult(
                False,
                f"Недостаточно товара. Доступно: {available} шт.",
                None
            )

        cart_item = self.cart_repo.add_to_cart(
            session,
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=product.unit_price or Decimal('0'),
            product_name = product.product_name
        )

        total = (product.unit_price or Decimal('0')) * quantity
        return AddProductResult(
            True,
            f"Добавлено: {product.product_name} x{quantity} = ${float(total):.2f}",
            cart_item
        )

    def remove_product(
            self,
            session: Session,
            customer_id: str,
            product_id: int,
            quantity: Optional[int] = None
    ) -> tuple[bool, str]:
        cart_item = self.cart_repo.get_by_customer_and_product(
            session, customer_id, product_id
        )

        if not cart_item:
            return False, "Товар не найден в корзине"

        if quantity is None or quantity >= cart_item.quantity:
            success = self.cart_repo.delete_by_customer_and_product(
                session, customer_id, product_id
            )
            return success, "Товар полностью удален из корзины"

        if quantity <= 0:
            return False, "Количество должно быть больше 0"

        cart_item.quantity -= quantity
        session.add(cart_item)
        session.flush()

        return True, f"Количество уменьшено на {quantity}. Осталось: {cart_item.quantity}"

    def update_quantity(
            self,
            session: Session,
            customer_id: str,
            product_id: int,
            quantity: int
    ) -> UpdateQuantityResult:
        if quantity <= 0:
            success, message = self.remove_product(session, customer_id, product_id)
            return UpdateQuantityResult(success, message, None)

        product = self._validate_product_exists(session, product_id)
        if not product:
            return UpdateQuantityResult(False, "Товар не найден или снят с производства", None)

        if quantity > (product.units_in_stock or 0):
            return UpdateQuantityResult(
                False,
                f"Недостаточно товара. Доступно: {product.units_in_stock} шт.",
                None
            )

        cart_item = self.cart_repo.update_quantity(
            session, customer_id, product_id, quantity
        )

        if cart_item:
            return UpdateQuantityResult(
                True,
                f"Количество обновлено: {product.product_name} x{quantity}",
                cart_item
            )
        return UpdateQuantityResult(False, "Товар не найден в корзине", None)

    def clear_cart(self, session: Session, customer_id: str) -> int:
        return self.cart_repo.clear_cart(session, customer_id)

    def get_cart_total(self, session: Session, customer_id: str) -> Decimal:
        return self.cart_repo.get_cart_total(session, customer_id)

    def get_cart_summary(self, session: Session, customer_id: str) -> Dict[str, Any]:
        cart_items = self.get_cart(session, customer_id)

        items_data = []
        total = Decimal('0')

        for item in cart_items:
            item_total = item.total
            total += item_total
            items_data.append({
                'product_id': item.product_id,
                'product_name': item.product.product_name,
                'unit_price': item.unit_price,
                'quantity': item.quantity,
                'total': item_total,
                'in_stock': item.product.units_in_stock
            })

        return {
            'items': items_data,
            'items_count': len(cart_items),
            'total_quantity': sum(item.quantity for item in cart_items),
            'total': total,
            'is_empty': len(cart_items) == 0
        }

    def validate_cart_stock(self, session: Session, customer_id: str) -> tuple[bool, List[Dict]]:

        cart_items = self.get_cart(session, customer_id)
        issues = []

        for item in cart_items:
            if (item.product.units_in_stock or 0) < item.quantity:
                issues.append({
                    'product_id': item.product_id,
                    'product_name': item.product.product_name,
                    'required': item.quantity,
                    'available': item.product.units_in_stock or 0,
                    'shortage': item.quantity - (item.product.units_in_stock or 0)
                })

        return len(issues) == 0, issues

    def get_cart_item(
            self,
            session: Session,
            customer_id: str,
            product_id: int
    ) -> Optional[CartItem]:
        return self.cart_repo.get_by_customer_and_product(
            session, customer_id, product_id
        )