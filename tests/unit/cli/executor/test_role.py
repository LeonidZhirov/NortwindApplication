# tests/cli/executor/test_role.py
from unittest.mock import Mock, patch
import pytest

from cli.executor.role import ExecutorRole


class TestExecutorRole:
    @pytest.fixture
    def mock_cli_context(self):
        context = Mock()
        context.clear_screen = Mock()
        context.wait_for_key = Mock()
        context.display_header = Mock()
        return context

    @pytest.fixture
    def role(self, mock_cli_context):
        return ExecutorRole(mock_cli_context)

    def test_get_role_name(self, role):
        assert "ИСПОЛНИТЕЛЯ" in role.get_role_name()

    def test_get_menu_items(self, role):
        menu = role.get_menu_items()
        expected_keys = ['1', '2', '3', '4', '5', '6', '7']
        for key in expected_keys:
            assert key in menu

    def test_get_status_info(self, role, session, test_order, test_stock_alert, test_product):
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        with patch.object(role._session_manager, 'session') as mock_session:
            mock_session.return_value.__enter__.return_value = session
            status = role.get_status_info()

            assert "Новых заказов: 1" in status
            assert "Активных уведомлений: 1" in status
            assert "Товаров с низким остатком: 1" in status

    def test_get_status_info_no_data(self, role, session):
        with patch.object(role._session_manager, 'session') as mock_session:
            mock_session.return_value.__enter__.return_value = session
            status = role.get_status_info()

            assert "Новых заказов: 0" in status
            assert "Активных уведомлений: 0" in status
            assert "Товаров с низким остатком: 0" in status

    def test_with_session(self):
        mock_context = Mock()
        role = ExecutorRole(mock_context)

        mock_session = Mock()
        mock_handler = Mock()
        mock_handler_class = Mock(return_value=mock_handler)

        with patch.object(role._session_manager, 'session') as mock_session_method:
            mock_session_method.return_value.__enter__.return_value = mock_session

            wrapper = role._with_session(mock_handler_class)
            wrapper()

            mock_handler_class.assert_called_once_with(mock_session)
            mock_handler.handle.assert_called_once()

    @patch('builtins.input')
    def test_run(self, mock_input, role):
        role._display_menu = Mock()
        role._execute_action = Mock(return_value=False)
        mock_input.return_value = "0"

        role.run()

        role._display_menu.assert_called()
        role._execute_action.assert_called_with("0")