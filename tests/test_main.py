"""Тесты для главного модуля программы."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.main import ask_status, format_date, format_transaction, get_source_name, main, mask_account


class TestFormatDate:
    """Тесты функции format_date."""

    def test_format_date(self) -> None:
        """Тест форматирования полной даты."""
        assert format_date("2019-12-08T00:00:00.000000") == "08.12.2019"

    def test_format_date_short(self) -> None:
        """Тест форматирования короткой строки."""
        assert format_date("short") == "short"


class TestMaskAccount:
    """Тесты функции mask_account."""

    def test_mask_account_number(self) -> None:
        """Тест маскирования номера счёта."""
        result: str = mask_account("Счет 12345678901234567890")
        assert result == "Счет **7890"

    def test_mask_card(self) -> None:
        """Тест маскирования номера карты."""
        result: str = mask_account("Visa Platinum 7492650272063783")
        assert result == "Visa Platinum 74** **** 3783"

    def test_mask_empty(self) -> None:
        """Тест маскирования пустой строки."""
        assert mask_account("") == ""

    def test_mask_unknown(self) -> None:
        """Тест маскирования неизвестного формата."""
        assert mask_account("Unknown") == "Unknown"


class TestFormatTransaction:
    """Тесты функции format_transaction."""

    def test_format_with_from_and_to(self) -> None:
        """Тест форматирования транзакции с полями from и to."""
        transaction: dict[str, Any] = {
            "date": "2019-07-03T18:35:29.512364",
            "description": "Перевод организации",
            "from": "Visa Platinum 7492650272063783",
            "to": "Счет 2935003472063783",
            "operationAmount": {
                "amount": "8200.00",
                "currency": {"name": "RUB"},
            },
        }
        result: str = format_transaction(transaction)
        assert "03.07.2019" in result
        assert "Перевод организации" in result
        assert "8200.00 RUB" in result
        assert "->" in result

    def test_format_with_to_only(self) -> None:
        """Тест форматирования транзакции только с полем to."""
        transaction: dict[str, Any] = {
            "date": "2019-12-08T00:00:00.000000",
            "description": "Открытие вклада",
            "to": "Счет 4321003472063783",
            "operationAmount": {
                "amount": "40542.00",
                "currency": {"name": "руб."},
            },
        }
        result: str = format_transaction(transaction)
        assert "08.12.2019" in result
        assert "Открытие вклада" in result
        assert "40542.00 руб." in result


class TestGetSourceName:
    """Тесты функции get_source_name."""

    def test_json(self) -> None:
        """Тест получения имени для JSON."""
        assert get_source_name("1") == "JSON"

    def test_csv(self) -> None:
        """Тест получения имени для CSV."""
        assert get_source_name("2") == "CSV"

    def test_xlsx(self) -> None:
        """Тест получения имени для XLSX."""
        assert get_source_name("3") == "XLSX"

    def test_invalid(self) -> None:
        """Тест получения имени для неверного значения."""
        assert get_source_name("4") == ""


class TestAskStatus:
    """Тесты функции ask_status."""

    @patch("builtins.input")
    def test_valid_status(self, mock_input: MagicMock) -> None:
        """Тест запроса валидного статуса."""
        mock_input.return_value = "executed"
        result: str = ask_status()
        assert result == "EXECUTED"

    @patch("builtins.input")
    def test_invalid_then_valid(self, mock_input: MagicMock) -> None:
        """Тест запроса статуса после неверного ввода."""
        mock_input.side_effect = ["test", "EXECUTED"]
        result: str = ask_status()
        assert result == "EXECUTED"


class TestMain:
    """Тесты основной функции main."""

    @patch("src.main.read_json_file")
    @patch("builtins.input")
    def test_main_json_basic(
        self,
        mock_input: MagicMock,
        mock_read_json: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с JSON-файлом."""
        mock_read_json.return_value = [
            {
                "id": 1,
                "description": "Перевод организации",
                "state": "EXECUTED",
                "date": "2019-07-03T18:35:29.512364",
                "to": "Счет 4321",
                "operationAmount": {
                    "amount": "8200.00",
                    "currency": {"name": "RUB", "code": "RUB"},
                },
            }
        ]
        mock_input.side_effect = [
            "1",
            "data/operations.json",
            "EXECUTED",
            "нет",
            "нет",
            "нет",
        ]
        main()
        captured = capsys.readouterr()
        assert "Для обработки выбран JSON-файл" in captured.out
        assert "Всего банковских операций в выборке: 1" in captured.out

    @patch("src.main.read_json_file")
    @patch("builtins.input")
    def test_main_invalid_status(
        self,
        mock_input: MagicMock,
        mock_read_json: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с неверным статусом."""
        mock_read_json.return_value = []
        mock_input.side_effect = [
            "1",
            "data/operations.json",
            "test",
            "EXECUTED",
            "нет",
            "нет",
            "нет",
        ]
        main()
        captured = capsys.readouterr()
        assert 'Статус операции "test" недоступен' in captured.out

    @patch("src.main.read_json_file")
    @patch("builtins.input")
    def test_main_empty_result(
        self,
        mock_input: MagicMock,
        mock_read_json: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с пустым результатом."""
        mock_read_json.return_value = []
        mock_input.side_effect = [
            "1",
            "data/operations.json",
            "EXECUTED",
            "нет",
            "нет",
            "нет",
        ]
        main()
        captured = capsys.readouterr()
        assert "Не найдено ни одной транзакции" in captured.out

    @patch("src.main.transactions")
    @patch("builtins.input")
    def test_main_csv_source(
        self,
        mock_input: MagicMock,
        mock_transactions: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с CSV-файлом."""
        mock_transactions.return_value = []
        mock_input.side_effect = [
            "2",
            "data/transactions.csv",
            "CANCELED",
            "нет",
            "нет",
            "нет",
        ]
        main()
        captured = capsys.readouterr()
        assert "Для обработки выбран CSV-файл" in captured.out

    @patch("src.main.transactions_ecxel")
    @patch("builtins.input")
    def test_main_xlsx_source(
        self,
        mock_input: MagicMock,
        mock_transactions_ecxel: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с XLSX-файлом."""
        mock_transactions_ecxel.return_value = []
        mock_input.side_effect = [
            "3",
            "data/transactions.xlsx",
            "PENDING",
            "нет",
            "нет",
            "нет",
        ]
        main()
        captured = capsys.readouterr()
        assert "Для обработки выбран XLSX-файл" in captured.out

    @patch("src.main.read_json_file")
    @patch("builtins.input")
    def test_main_with_sorting(
        self,
        mock_input: MagicMock,
        mock_read_json: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с сортировкой."""
        mock_read_json.return_value = [
            {
                "id": 1,
                "description": "Перевод",
                "state": "EXECUTED",
                "date": "2019-12-08T00:00:00.000000",
                "to": "Счет 4321",
                "operationAmount": {
                    "amount": "100.00",
                    "currency": {"name": "RUB", "code": "RUB"},
                },
            },
            {
                "id": 2,
                "description": "Перевод",
                "state": "EXECUTED",
                "date": "2019-07-03T00:00:00.000000",
                "to": "Счет 1234",
                "operationAmount": {
                    "amount": "200.00",
                    "currency": {"name": "RUB", "code": "RUB"},
                },
            },
        ]
        mock_input.side_effect = [
            "1",
            "data/operations.json",
            "EXECUTED",
            "да",
            "по возрастанию",
            "нет",
            "нет",
        ]
        main()
        captured = capsys.readouterr()
        assert "03.07.2019" in captured.out
        assert "08.12.2019" in captured.out

    @patch("src.main.process_bank_search")
    @patch("src.main.read_json_file")
    @patch("builtins.input")
    def test_main_with_search(
        self,
        mock_input: MagicMock,
        mock_read_json: MagicMock,
        mock_search: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с поиском по слову."""
        mock_read_json.return_value = [
            {
                "id": 1,
                "description": "Перевод",
                "state": "EXECUTED",
                "date": "2019-07-03T18:35:29.512364",
                "to": "Счет 4321",
                "operationAmount": {
                    "amount": "8200.00",
                    "currency": {"name": "RUB", "code": "RUB"},
                },
            }
        ]
        mock_search.return_value = []
        mock_input.side_effect = [
            "1",
            "data/operations.json",
            "EXECUTED",
            "нет",
            "нет",
            "да",
            "слово",
        ]
        main()
        mock_search.assert_called_once()
        captured = capsys.readouterr()
        assert "Не найдено ни одной транзакции" in captured.out

    @patch("src.main.read_json_file")
    @patch("builtins.input")
    def test_main_rub_filter(
        self,
        mock_input: MagicMock,
        mock_read_json: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест основной функции с фильтром по рублям."""
        mock_read_json.return_value = [
            {
                "id": 1,
                "description": "Перевод",
                "state": "EXECUTED",
                "date": "2019-07-03T18:35:29.512364",
                "to": "Счет 4321",
                "operationAmount": {
                    "amount": "100.00",
                    "currency": {"name": "USD", "code": "USD"},
                },
            }
        ]
        mock_input.side_effect = [
            "1",
            "data/operations.json",
            "EXECUTED",
            "нет",
            "да",
            "нет",
        ]
        main()
        captured = capsys.readouterr()
        assert "Не найдено ни одной транзакции" in captured.out
