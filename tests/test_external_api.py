# -*- coding: utf-8 -*-
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

from src.external_api import convert_transaction_to_rub, get_exchange_rate


class TestGetExchangeRate:
    """Тесты для функции получения курса валюты."""

    @patch("src.external_api.requests.get")
    @patch.dict("os.environ", {"API": "test_api_key"})
    def test_get_exchange_rate_success(self, mock_get: MagicMock) -> None:
        """Тест: успешное получение курса USD к RUB."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "base": "USD",
            "date": "2026-06-21",
            "rates": {"RUB": 80.5},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_exchange_rate("USD")

        assert result == 80.5
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        # Обновлены ожидаемые значения в соответствии с исправлениями в коде
        assert call_args.kwargs["headers"] == {"apikey": "test_api_key"}
        assert call_args.kwargs["params"] == {"base": "USD", "symbols": "RUB"}


class TestConvertTransactionToRub:
    """Тесты для функции конвертации транзакции в рубли."""

    def test_convert_rub_transaction(self) -> None:
        """Тест: транзакция в рублях возвращается без изменений."""
        transaction = {
            "operationAmount": {
                "amount": "1000.00",
                "currency": {"name": "руб.", "code": "RUB"},
            }
        }
        result = convert_transaction_to_rub(transaction)
        assert result == 1000.0

    @patch("src.external_api.get_exchange_rate")
    def test_convert_usd_transaction(self, mock_get_rate: MagicMock) -> None:
        """Тест: конвертация USD в RUB через API."""
        mock_get_rate.return_value = 80.5
        transaction = {
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "USD", "code": "USD"},
            }
        }
        result = convert_transaction_to_rub(transaction)
        assert result == 8050.0
        mock_get_rate.assert_called_once_with("USD")

    @patch("src.external_api.get_exchange_rate")
    def test_convert_eur_transaction(self, mock_get_rate: MagicMock) -> None:
        """Тест: конвертация EUR в RUB через API."""
        mock_get_rate.return_value = 90.0
        transaction = {
            "operationAmount": {
                "amount": "50.00",
                "currency": {"name": "EUR", "code": "EUR"},
            }
        }
        result = convert_transaction_to_rub(transaction)
        assert result == 4500.0
        mock_get_rate.assert_called_once_with("EUR")

    def test_convert_unknown_currency(self) -> None:
        """Тест: неизвестная валюта → возвращается 0.0."""
        transaction = {
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "Yuan", "code": "CNY"},
            }
        }
        result = convert_transaction_to_rub(transaction)
        assert result == 0.0

    def test_convert_transaction_missing_keys(self) -> None:
        """Тест: отсутствуют ключи в транзакции (покрытие веток get())."""
        transaction: Dict[str, Any] = {}
        result = convert_transaction_to_rub(transaction)
        assert result == 0.0
