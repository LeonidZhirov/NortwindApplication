from dataclasses import dataclass
from decimal import Decimal

@dataclass
class CartItem:
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity