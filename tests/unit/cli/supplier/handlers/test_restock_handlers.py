# tests/cli/supplier/handlers/test_restock_handlers.py
from unittest.mock import Mock, patch

from cli.supplier.handlers import ShowRestockRequestsHandler, RestockProductsHandler

class TestShowRestockRequestsHandler:
    def test_handle_no_alerts(self, capsys, session, test_supplier):
        handler = ShowRestockRequestsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Нет активных заявок на пополнение" in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_alerts(self, capsys, session, test_supplier, test_product, test_stock_alert):
        handler = ShowRestockRequestsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert str(test_stock_alert.alert_id) in captured.out
        handler._wait.assert_called_once()

    @patch('builtins.input')
    def test_auto_restock_all(self, mock_input, session, test_supplier, test_product, test_stock_alert):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = ShowRestockRequestsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=1)

        handler.handle(supplier_id=test_supplier.supplier_id)

        session.refresh(test_product)
        assert test_product.units_in_stock > 3
        handler._wait.assert_called_once()

class TestRestockProductsHandler:
    def test_handle_no_products(self, capsys, session, test_supplier):
        from models.product_model import Product
        session.query(Product).filter(
            Product.supplier_id == test_supplier.supplier_id
        ).delete()
        session.flush()

        handler = RestockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "У вас пока нет товаров" in captured.out
        handler._wait.assert_called_once()

    def test_handle_no_low_stock(self, capsys, session, test_supplier, test_product):
        test_product.units_in_stock = 100
        test_product.reorder_level = 10
        session.flush()

        handler = RestockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Все товары в достаточном количестве" in captured.out
        handler._wait.assert_called_once()

    @patch('builtins.input')
    def test_handle_with_low_stock_cancel(self, mock_input, capsys, session, test_supplier, test_product):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = RestockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        mock_input.return_value = "0"

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert test_product.product_name in captured.out
        handler._wait.assert_not_called()

    @patch('builtins.input')
    def test_handle_with_low_stock_restock(self, mock_input, session, test_supplier, test_product):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = RestockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        mock_input.side_effect = [
            str(test_product.product_id),
            "20"
        ]

        handler.handle(supplier_id=test_supplier.supplier_id)

        session.refresh(test_product)
        assert test_product.units_in_stock == 23
        handler._wait.assert_called_once()

    @patch('builtins.input')
    def test_handle_with_low_stock_invalid_product(self, mock_input, capsys, session, test_supplier, test_product):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = RestockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        mock_input.return_value = "999"

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Товар не требует пополнения или не найден" in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_low_stock_zero_quantity(self, capsys, session, test_supplier, test_product):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = RestockProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler._input_int = Mock(side_effect=[
            test_product.product_id,
            0,
            0
        ])

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Количество должно быть больше 0" in captured.out
        handler._wait.assert_called_once()