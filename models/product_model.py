from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Product:
    product_id: int
    product_name: str
    unit_price: Decimal
    units_in_stock: int
    reorder_level: int
    discontinued: int

    def __str__(self):
        return f"{self.product_id:>3} | {self.product_name:<40} | ${self.unit_price:>8.2f} | {self.units_in_stock:>5} шт."