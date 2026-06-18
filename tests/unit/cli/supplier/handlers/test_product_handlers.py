# tests/cli/supplier/handlers/test_product_handlers.py
import pytest
from unittest.mock import Mock, patch

from cli.supplier.handlers import ShowMyProductsHandler, SearchMyProductsHandler


class TestShowMyProductsHandler:
    def test_handle_no_products(self, capsys, session, test_supplier):
        from models.product_model import Product
        session.query(Product).filter(
            Product.supplier_id == test_supplier.supplier_id
        ).delete()
        session.flush()

        handler = ShowMyProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "У вас пока нет товаров" in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_products(self, capsys, session, test_supplier, test_product):
        handler = ShowMyProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert test_product.product_name in captured.out
        handler._wait.assert_called_once()


class TestSearchMyProductsHandler:
    @patch('builtins.input')
    def test_search_found(self, mock_input, capsys, session, test_supplier, test_product):
        mock_input.return_value = "Test"

        handler = SearchMyProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Найдено товаров: 1" in captured.out
        handler._wait.assert_called_once()

    @patch('builtins.input')
    def test_search_not_found(self, mock_input, capsys, session, test_supplier, test_product):
        mock_input.return_value = "NotFound"

        handler = SearchMyProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "не найдены" in captured.out
        handler._wait.assert_called_once()

    @patch('builtins.input')
    def test_search_all(self, mock_input, capsys, session, test_supplier, test_product):
        mock_input.return_value = "*"

        handler = SearchMyProductsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Найдено товаров: 1" in captured.out
        handler._wait.assert_called_once()