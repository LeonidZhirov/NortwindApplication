from unittest.mock import Mock

from cli.executor.handlers import ShowLowStockProductsHandler
from models.product_model import Product


class TestShowLowStockProductsHandler:
    def test_handle_with_low_stock(self, capsys, session, test_product):
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        handler = ShowLowStockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert test_product.product_name in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_low_stock_multiple_products(self, capsys, session):
        product1 = Product(
            product_name="Low Stock 1",
            unit_price=10.0,
            units_in_stock=3,
            reorder_level=10,
            discontinued=0
        )
        product2 = Product(
            product_name="Low Stock 2",
            unit_price=15.0,
            units_in_stock=5,
            reorder_level=10,
            discontinued=0
        )
        session.add_all([product1, product2])
        session.flush()

        handler = ShowLowStockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert "Low Stock 1" in captured.out
        assert "Low Stock 2" in captured.out
        handler._wait.assert_called_once()

    def test_handle_no_low_stock(self, capsys, session, test_product):
        test_product.units_in_stock = 100
        test_product.reorder_level = 10
        session.flush()

        handler = ShowLowStockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert "Все товары в достаточном количестве" in captured.out
        handler._wait.assert_called_once()