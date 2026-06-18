# tests/cli/customer/test_role.py
import pytest
from unittest.mock import Mock, patch

from cli.customer.role import CustomerRole


class TestCustomerRole:
    @pytest.fixture
    def mock_cli_context(self):
        context = Mock()
        context.clear_screen = Mock()
        context.wait_for_key = Mock()
        context.display_header = Mock()
        return context

    @pytest.fixture
    def role(self, mock_cli_context):
        return CustomerRole(mock_cli_context)

    def test_get_role_name(self, role):
        assert "ПОКУПАТЕЛЯ" in role.get_role_name()

    def test_get_menu_items(self, role):
        menu = role.get_menu_items()
        assert '1' in menu
        assert '2' in menu
        assert '3' in menu
        assert '4' in menu
        assert '5' in menu
        assert '6' in menu
        assert '7' in menu
        assert '8' in menu

    def test_get_status_info_no_customer(self, role):
        status = role.get_status_info()
        assert "Клиент не выбран" in status

    @patch('cli.customer.role.SelectCustomerHandler')
    def test_select_customer_interactive_success(self, mock_handler, role, session):
        mock_handler.return_value.handle.return_value = "TEST1"

        result = role._select_customer_interactive()

        assert result is True
        assert role._customer_id == "TEST1"

    @patch('cli.customer.role.SelectCustomerHandler')
    def test_select_customer_interactive_cancel(self, mock_handler, role, session):
        mock_handler.return_value.handle.return_value = None

        result = role._select_customer_interactive()

        assert result is False
        assert role._customer_id is None