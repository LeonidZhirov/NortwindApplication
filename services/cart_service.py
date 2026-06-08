from decimal import Decimal
from typing import List
from models.cart_item_model import CartItem


class CartService:
    def __init__(self):
        self._items: List[CartItem] = []

    def add_item(self, item: CartItem):
        self._items.append(item)

    def get_items(self) -> List[CartItem]:
        return self._items.copy()

    def clear(self):
        self._items.clear()

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def get_total(self) -> Decimal:
        return Decimal(sum(item.total for item in self._items))

    def get_item_count(self) -> int:
        return len(self._items)