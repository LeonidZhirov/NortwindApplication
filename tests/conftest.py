# tests/conftest.py
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from models import (
    Base,
    Customer,
    Product,
    CartItem,
    Order,
    StockAlert,
    OrderDetail,
    Supplier
)


TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


@pytest.fixture
def test_customer(session) -> Customer:
    customer = Customer(
        customer_id="TEST1",
        company_name="Test Company",
        contact_name="Test Contact",
        country="Test Country"
    )
    session.add(customer)
    session.flush()
    return customer


@pytest.fixture
def test_product(session, test_supplier) -> Product:
    product = Product(
        product_name="Test Product",
        unit_price=10.0,
        units_in_stock=100,
        supplier_id=test_supplier.supplier_id,
        discontinued=0
    )
    session.add(product)
    session.flush()
    return product


@pytest.fixture
def test_cart_item(session, test_customer, test_product) -> CartItem:
    cart_item = CartItem(
        customer_id=test_customer.customer_id,
        product_id=test_product.product_id,
        product_name=test_product.product_name,
        quantity=5,
        unit_price=10.0
    )
    session.add(cart_item)
    session.flush()
    return cart_item

@pytest.fixture
def test_order(session, test_customer, test_product):
    order = Order(
        customer_id=test_customer.customer_id,
        employee_id=1,
        order_date=date.today()
    )
    session.add(order)
    session.flush()

    detail = OrderDetail(
        order_id=order.order_id,
        product_id=test_product.product_id,
        quantity=2,
        unit_price=10.0,
        discount=0
    )
    session.add(detail)
    session.flush()

    return order


@pytest.fixture
def test_shipped_order(session, test_customer, test_product):
    order = Order(
        customer_id=test_customer.customer_id,
        employee_id=1,
        order_date=date.today(),
        shipped_date=date.today()
    )
    session.add(order)
    session.flush()

    detail = OrderDetail(
        order_id=order.order_id,
        product_id=test_product.product_id,
        quantity=2,
        unit_price=10.0,
        discount=0
    )
    session.add(detail)
    session.flush()

    return order


@pytest.fixture
def test_stock_alert(session, test_product, test_supplier):
    alert = StockAlert(
        product_id=test_product.product_id,
        current_stock=5,
        reorder_level=10,
        supplier_id=test_supplier.supplier_id,
        status='pending'
    )
    session.add(alert)
    session.flush()
    return alert

@pytest.fixture
def test_supplier(session) -> Supplier:
    supplier = Supplier(
        company_name="Test Supplier",
        contact_name="Test Contact",
        country="Test Country"
    )
    session.add(supplier)
    session.flush()
    return supplier