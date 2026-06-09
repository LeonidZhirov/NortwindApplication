from sqlalchemy import Table, Column, Integer, ForeignKey
from models.base import Base

order_cart_items = Table(
    'order_cart_items',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.order_id'), primary_key=True),
    Column('cart_item_id', Integer, ForeignKey('cart_items.cart_item_id'), primary_key=True)
)