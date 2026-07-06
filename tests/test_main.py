# -*- coding: utf-8 -*-
"""Тесты для модуля main со 100% покрытием."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.bank_search import process_bank_search as real_process_bank_search
from src.generators import filter_by_currency as real_filter_by_currency
from src.main import (ask_status, ask_yes_no, calculate_total_in_rub, format_date_iso, format_transaction,
                      get_all_descriptions, get_amount_in_rub, get_source_name, is_valid_card_number, load_data, main,
                      mask_from_to_field, show_exchange_rates, validate_card_numbers_in_data)

# ==================== ТЕСТОВЫЕ ДАННЫЕ ====================

SAMPLE_TRANSACTION: dict[str, Any] = {
    "id": 1,
    "state": "EXECUTED",
    "date": "2019-07-03T18:35:29.512364",
    "operationAmount": {
        "amount": "130.00",
        "currency": {"name": "USD", "code": "USD"},
    },
    "description": "Перевод организации",
    "from": "Visa Platinum 7492650272063783",
    "to": "Счет 12345678901234567890",
}

SAMPLE_TRANSACTION_RUB: dict[str, Any] = {
    "id": 2,
    "state": "EXECUTED",
    "date": "2019-12-08T00:00:00.000000",
    "operationAmount": {
        "amount": "40542.00",
        "currency": {"name": "руб.", "code": "RUB"},
    },
    "description": "Открытие вклада",
    "to": "Счет 98765432109876543210",
}


# ==================== ТЕСТЫ ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ ====================


class TestIsValidCardNumber:
    """Тесты функции is_valid_card_number."""

    @pytest.mark.parametrize(
        "card_number, expected",
        [
            ("7492650272063783", True),
            ("1234567890123456", True),
            ("123", False),
            ("", False),
            (1234567890123456, False),  # Число — не строка
            (None, False),  # None — не строка
            ([], False),
        ],
    )
    def test_is_valid_card_number(self, card_number: str, expected: bool) -> None:
        """Проверяет валидацию номера карты."""
        assert is_valid_card_number(card_number) is expected


class TestMaskFromToField:
    """Тесты функции mask_from_to_field."""

    @pytest.mark.parametrize(
        "field_value, expected_substring",
        [
            ("", ""),
            ("Счет 12345678901234567890", "Счет"),
            ("Visa Platinum 7492650272063783", "Visa Platinum"),
            ("Visa Platinum 123", "Visa Platinum"),
            ("ОдноСлово", "ОдноСлово"),
            ("Visa Platinum 12345", "Visa Platinum"),  # 5 цифр вместо 16
            ("MasterCard 123456789012345", "MasterCard"),  # 15 цифр
        ],
    )
    def test_mask_from_to_field(self, field_value: str, expected_substring: str) -> None:
        """Проверяет маскирование полей from/to."""
        result = mask_from_to_field(field_value)
        if expected_substring:
            assert expected_substring in result

    @patch("src.main.mask_account_card")
    @patch("src.main.is_valid_card_number")
    def test_mask_from_to_field_try_branch(
        self,
        mock_is_valid: MagicMock,
        mock_mask_account: MagicMock,
    ) -> None:
        """🆕 Покрывает строку: return mask_account_card(field_value)"""
        # 🆕 Подменяем is_valid_card_number чтобы возвращал True
        # (обходим проверку длины 16)
        mock_is_valid.return_value = True

        # 🆕 mask_account_card успешно маскирует
        mock_mask_account.return_value = "Maestro 1234 56** **** 7890"

        # Вход: карта с длиной НЕ 16 (например, 15 цифр)
        field_value = "Maestro 123456789012345"

        result = mask_from_to_field(field_value)

        # Проверяем результат
        assert result == "Maestro 1234 56** **** 7890"

        # 🆕 Явно проверяем, что mask_account_card был вызван
        mock_mask_account.assert_called_once_with(field_value)

    @patch("src.main.mask_account_card")
    @patch("src.main.is_valid_card_number")
    def test_mask_from_to_field_except_branch(
        self,
        mock_is_valid: MagicMock,
        mock_mask_account: MagicMock,
    ) -> None:
        """🆕 Покрывает строку: except ValueError: return field_value"""
        # 🆕 Подменяем is_valid_card_number чтобы возвращал True
        mock_is_valid.return_value = True

        # 🆕 mask_account_card ВЫБРАСЫВАЕТ ValueError
        mock_mask_account.side_effect = ValueError("Unsupported card type")

        # Вход: карта с длиной НЕ 16
        field_value = "UnknownCard 123456789012345"

        result = mask_from_to_field(field_value)

        # 🆕 При ошибке возвращается исходное значение
        assert result == field_value

        # 🆕 Проверяем, что mask_account_card был вызван
        mock_mask_account.assert_called_once_with(field_value)


class TestFormatDateIso:
    """Тесты функции format_date_iso."""

    @pytest.mark.parametrize(
        "date_string, expected",
        [
            ("2019-07-03T18:35:29.512364", "03.07.2019"),
            ("2019-12-08", "08.12.2019"),
            ("", ""),
            ("short", "short"),
            ("2019-13-45", "45.13.2019"),  # Несуществующая дата — fallback
            ("abcd-ef-gh", "gh.ef.abcd"),  # Буквы вместо цифр — fallback
        ],
    )
    def test_format_date_iso(self, date_string: str, expected: str) -> None:
        """Проверяет форматирование даты."""
        assert format_date_iso(date_string) == expected


class TestGetAmountInRub:
    """Тесты функции get_amount_in_rub."""

    @patch("src.main.convert_transaction_to_rub")
    def test_get_amount_in_rub_success(self, mock_convert: MagicMock) -> None:
        """Проверяет успешную конвертацию."""
        mock_convert.return_value = 9100.0
        assert get_amount_in_rub(SAMPLE_TRANSACTION) == 9100.0

    @patch("src.main.convert_transaction_to_rub")
    def test_get_amount_in_rub_error(self, mock_convert: MagicMock) -> None:
        """Проверяет обработку ошибки конвертации."""
        mock_convert.side_effect = Exception("API error")
        assert get_amount_in_rub(SAMPLE_TRANSACTION) is None


class TestFormatTransaction:
    """Тесты функции format_transaction."""

    def test_format_transaction_without_conversion(self) -> None:
        """Проверяет форматирование без конвертации."""
        result = format_transaction(SAMPLE_TRANSACTION)
        assert "03.07.2019" in result
        assert "Перевод организации" in result
        assert "130.00" in result
        assert "USD" in result

    @patch("src.main.get_amount_in_rub")
    def test_format_transaction_with_conversion(self, mock_amount: MagicMock) -> None:
        """Проверяет форматирование с конвертацией."""
        mock_amount.return_value = 11830.0
        result = format_transaction(SAMPLE_TRANSACTION, convert_to_rub=True)
        assert "≈ 11830.00 руб." in result

    @patch("src.main.get_amount_in_rub")
    def test_format_transaction_rub_no_conversion(self, mock_amount: MagicMock) -> None:
        """Проверяет, что RUB не конвертируется."""
        result = format_transaction(SAMPLE_TRANSACTION_RUB, convert_to_rub=True)
        mock_amount.assert_not_called()
        assert "40542.00" in result

    @patch("src.main.get_amount_in_rub")
    def test_format_transaction_conversion_error(self, mock_amount: MagicMock) -> None:
        """Проверяет обработку ошибки конвертации при форматировании."""
        mock_amount.return_value = None
        result = format_transaction(SAMPLE_TRANSACTION, convert_to_rub=True)
        assert "130.00" in result
        assert "USD" in result


class TestGetAllDescriptions:
    """Тесты функции get_all_descriptions."""

    def test_get_all_descriptions(self) -> None:
        """Проверяет получение описаний через генератор."""
        transactions = [SAMPLE_TRANSACTION, SAMPLE_TRANSACTION_RUB]
        result = get_all_descriptions(transactions)
        assert result == ["Перевод организации", "Открытие вклада"]

    def test_get_all_descriptions_empty(self) -> None:
        """Проверяет пустой список."""
        assert get_all_descriptions([]) == []


class TestValidateCardNumbersInData:
    """Тесты функции validate_card_numbers_in_data."""

    def test_validate_card_numbers_in_data(self) -> None:
        """Проверяет подсчёт валидных карт."""
        transactions = [SAMPLE_TRANSACTION, SAMPLE_TRANSACTION_RUB]
        result = validate_card_numbers_in_data(transactions)
        # 3 тестовые карты из card_number_generator + 1 реальная карта
        assert result >= 1


class TestCalculateTotalInRub:
    """Тесты функции calculate_total_in_rub."""

    @patch("src.main.get_amount_in_rub")
    def test_calculate_total_in_rub(self, mock_amount: MagicMock) -> None:
        """Проверяет подсчёт общей суммы."""
        mock_amount.side_effect = [9100.0, 40542.0]
        transactions = [SAMPLE_TRANSACTION, SAMPLE_TRANSACTION_RUB]
        result = calculate_total_in_rub(transactions)
        assert result == 49642.0

    @patch("src.main.get_amount_in_rub")
    def test_calculate_total_in_rub_with_none(self, mock_amount: MagicMock) -> None:
        """Проверяет обработку None в суммах."""
        mock_amount.side_effect = [None, 40542.0]
        transactions = [SAMPLE_TRANSACTION, SAMPLE_TRANSACTION_RUB]
        result = calculate_total_in_rub(transactions)
        assert result == 40542.0


class TestShowExchangeRates:
    """Тесты функции show_exchange_rates."""

    @patch("src.main.get_exchange_rate")
    def test_show_exchange_rates_success(self, mock_rate: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        """Проверяет вывод курсов при успехе."""
        mock_rate.side_effect = [91.0, 98.5]
        show_exchange_rates()
        output = capsys.readouterr().out
        assert "1 USD = 91.00 RUB" in output
        assert "1 EUR = 98.50 RUB" in output

    @patch("src.main.get_exchange_rate")
    def test_show_exchange_rates_error(self, mock_rate: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        """Проверяет обработку ошибок API."""
        mock_rate.side_effect = Exception("API error")
        show_exchange_rates()
        output = capsys.readouterr().out
        assert "не удалось получить курс" in output


# ==================== ТЕСТЫ ИНТЕРАКТИВА ====================


class TestAskYesNo:
    """Тесты функции ask_yes_no."""

    @pytest.mark.parametrize(
        "user_input, expected",
        [
            ("да", True),
            ("Да", True),
            ("ДА", True),
            ("yes", True),
            ("y", True),
            ("нет", False),
            ("", False),
            ("абв", False),
        ],
    )
    def test_ask_yes_no(self, user_input: str, expected: bool, capsys: pytest.CaptureFixture[str]) -> None:
        """Проверяет обработку ответов Да/Нет."""
        with patch("builtins.input", return_value=user_input):
            assert ask_yes_no("Вопрос?") is expected


class TestAskStatus:
    """Тесты функции ask_status."""

    def test_ask_status_valid_first_try(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Проверяет ввод валидного статуса с первого раза."""
        with patch("builtins.input", return_value="EXECUTED"):
            result = ask_status()
        assert result == "EXECUTED"

    def test_ask_status_case_insensitive(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Проверяет приведение к верхнему регистру."""
        with patch("builtins.input", return_value="executed"):
            result = ask_status()
        assert result == "EXECUTED"

    def test_ask_status_invalid_then_valid(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Проверяет повторный запрос при невалидном вводе."""
        with patch("builtins.input", side_effect=["test", "CANCELED"]):
            result = ask_status()
        assert result == "CANCELED"
        output = capsys.readouterr().out
        assert 'Статус операции "test" недоступен' in output


# ==================== ТЕСТЫ ЗАГРУЗКИ ДАННЫХ ====================


class TestLoadData:
    """Тесты функции load_data."""

    @patch("src.main.read_json_file")
    def test_load_data_json(self, mock_read: MagicMock) -> None:
        """Проверяет загрузку JSON."""
        mock_read.return_value = [{"id": 1}]
        result = load_data("1")
        assert result == [{"id": 1}]
        mock_read.assert_called_once()

    @patch("src.main.transactions")
    def test_load_data_csv(self, mock_read: MagicMock) -> None:
        """Проверяет загрузку CSV."""
        mock_read.return_value = [{"id": 2}]
        result = load_data("2")
        assert result == [{"id": 2}]
        mock_read.assert_called_once()

    @patch("src.main.transactions_ecxel")
    def test_load_data_xlsx(self, mock_read: MagicMock) -> None:
        """Проверяет загрузку XLSX."""
        mock_read.return_value = [{"id": 3}]
        result = load_data("3")
        assert result == [{"id": 3}]
        mock_read.assert_called_once()


class TestGetSourceName:
    """Тесты функции get_source_name."""

    @pytest.mark.parametrize(
        "choice, expected",
        [
            ("1", "JSON"),
            ("2", "CSV"),
            ("3", "XLSX"),
            ("4", ""),
        ],
    )
    def test_get_source_name(self, choice: str, expected: str) -> None:
        """Проверяет получение имени источника."""
        assert get_source_name(choice) == expected


# ==================== ТЕСТЫ ОСНОВНОЙ ФУНКЦИИ ====================


class TestMain:
    """Тесты функции main."""

    # ==================== ТЕСТ 1: ПОЛНЫЙ СЦЕНАРИЙ СО ВСЕМИ "ДА" ====================

    @patch("src.main.calculate_total_in_rub", return_value=11830.0)
    @patch("src.main.show_exchange_rates")
    @patch("src.main.process_bank_search", wraps=real_process_bank_search)
    @patch("src.main.filter_by_currency", wraps=real_filter_by_currency)
    @patch("src.main.sort_by_date")
    @patch("src.main.filter_by_state")
    @patch("src.main.load_data")
    @patch("builtins.input")
    def test_main_full_scenario(
        self,
        mock_input: MagicMock,
        mock_load: MagicMock,
        mock_filter_state: MagicMock,
        mock_sort: MagicMock,
        mock_filter_currency: MagicMock,
        mock_bank_search: MagicMock,
        mock_rates: MagicMock,
        mock_total: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """🆕 Полный сценарий: все ветки с 'да' покрыты."""
        # ✅ Правильная последовательность ответов (ровно по вопросам main)
        mock_input.side_effect = [
            "1",  # 1. Выбор источника (JSON)
            "EXECUTED",  # 2. Статус
            "да",  # 3. Сортировать по дате? ДА
            "по убыванию",  # 4. Направление сортировки
            "да",  # 5. 🆕 Только рублёвые? ДА → filter_by_currency
            "да",  # 6. 🆕 Поиск по слову? ДА → input() + process_bank_search
            "Открытие",  # 7. 🆕 Слово для поиска
            "да",  # 8. 🆕 Конвертация в рубли? ДА
        ]

        # Настраиваем реальные данные с двумя валютами
        mock_load.return_value = [SAMPLE_TRANSACTION, SAMPLE_TRANSACTION_RUB]
        mock_filter_state.return_value = [SAMPLE_TRANSACTION, SAMPLE_TRANSACTION_RUB]
        mock_sort.return_value = [SAMPLE_TRANSACTION, SAMPLE_TRANSACTION_RUB]

        # filter_by_currency через wraps фильтрует реально → вернёт только RUB
        # process_bank_search через wraps фильтрует по слову "Открытие" → SAMPLE_TRANSACTION_RUB

        main()

        output = capsys.readouterr().out

        # Проверяем основные сообщения
        assert "Привет! Добро пожаловать" in output
        assert "Для обработки выбран JSON-файл" in output
        assert 'Операции отфильтрованы по статусу "EXECUTED"' in output
        assert "Всего банковских операций в выборке" in output

        # 🆕 Явные проверки, что функции БЫЛИ вызваны
        mock_filter_currency.assert_called_once()
        mock_bank_search.assert_called_once()
        mock_rates.assert_called_once()
        mock_total.assert_called_once()

    # ==================== ТЕСТ 2: ПУСТЫЕ ДАННЫЕ ====================

    @patch("src.main.filter_by_state")
    @patch("src.main.load_data")
    @patch("builtins.input")
    def test_main_empty_data(
        self,
        mock_input: MagicMock,
        mock_load: MagicMock,
        mock_filter_state: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Проверяет обработку пустых данных."""
        mock_input.side_effect = ["1", "EXECUTED"]
        mock_load.return_value = []

        main()

        output = capsys.readouterr().out
        assert "Файл пуст или не содержит данных" in output

    # ==================== ТЕСТ 3: НЕТ РЕЗУЛЬТАТОВ ====================

    @patch("src.main.filter_by_state")
    @patch("src.main.load_data")
    @patch("builtins.input")
    def test_main_no_results(
        self,
        mock_input: MagicMock,
        mock_load: MagicMock,
        mock_filter_state: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Проверяет сообщение при отсутствии результатов."""
        mock_input.side_effect = [
            "1",
            "EXECUTED",
            "нет",  # Сортировка
            "нет",  # Валюта
            "нет",  # Поиск
            "нет",  # Конвертация
        ]
        mock_load.return_value = [SAMPLE_TRANSACTION]
        mock_filter_state.return_value = []

        main()

        output = capsys.readouterr().out
        assert "Не найдено ни одной транзакции" in output

    # ==================== ТЕСТ 4: ТОЛЬКО КОНВЕРТАЦИЯ ====================

    @patch("src.main.show_exchange_rates")
    @patch("src.main.calculate_total_in_rub")
    @patch("src.main.process_bank_search")
    @patch("src.main.filter_by_currency")
    @patch("src.main.sort_by_date")
    @patch("src.main.filter_by_state")
    @patch("src.main.load_data")
    @patch("builtins.input")
    def test_main_with_conversion(
        self,
        mock_input: MagicMock,
        mock_load: MagicMock,
        mock_filter_state: MagicMock,
        mock_sort: MagicMock,
        mock_filter_currency: MagicMock,
        mock_bank_search: MagicMock,
        mock_total: MagicMock,
        mock_rates: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Проверяет сценарий только с конвертацией (остальное 'нет')."""
        mock_input.side_effect = [
            "1",
            "EXECUTED",
            "нет",  # Без сортировки
            "нет",  # Без рублёвых
            "нет",  # Без поиска
            "да",  # 🆕 Только конвертация
        ]
        mock_load.return_value = [SAMPLE_TRANSACTION]
        mock_filter_state.return_value = [SAMPLE_TRANSACTION]
        mock_sort.return_value = [SAMPLE_TRANSACTION]
        mock_filter_currency.return_value = iter([SAMPLE_TRANSACTION])
        mock_bank_search.return_value = [SAMPLE_TRANSACTION]
        mock_total.return_value = 11830.0

        main()

        output = capsys.readouterr().out
        assert "Общая сумма в рублях" in output
        mock_rates.assert_called_once()
        mock_total.assert_called_once()

    # ==================== ТЕСТ 5: НЕВАЛИДНЫЙ ВЫБОР ====================

    @patch("builtins.input")
    def test_main_invalid_choice_then_valid(self, mock_input: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        """Проверяет повторный запрос при невалидном выборе."""
        mock_input.side_effect = [
            "5",  # Невалидный
            "abc",  # Невалидный
            "1",  # Валидный
            "EXECUTED",
            "нет",  # Сортировка
            "нет",  # Валюта
            "нет",  # Поиск
            "нет",  # Конвертация
        ]

        with patch("src.main.load_data", return_value=[SAMPLE_TRANSACTION]):
            with patch("src.main.filter_by_state", return_value=[SAMPLE_TRANSACTION]):
                main()

        output = capsys.readouterr().out
        assert "Неверный ввод" in output

    # ==================== ТЕСТ 6: СОРТИРОВКА ПО ВОЗРАСТАНИЮ ====================

    @patch("src.main.sort_by_date")
    @patch("src.main.filter_by_state")
    @patch("src.main.load_data")
    @patch("builtins.input")
    def test_main_sort_ascending(
        self,
        mock_input: MagicMock,
        mock_load: MagicMock,
        mock_filter_state: MagicMock,
        mock_sort: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """🆕 Покрывает ветку сортировки по возрастанию."""
        mock_input.side_effect = [
            "1",
            "EXECUTED",
            "да",  # Сортировать
            "по возрастанию",  # 🆕 По возрастанию (reverse=False)
            "нет",
            "нет",
            "нет",
        ]
        mock_load.return_value = [SAMPLE_TRANSACTION]
        mock_filter_state.return_value = [SAMPLE_TRANSACTION]
        mock_sort.return_value = [SAMPLE_TRANSACTION]

        main()

        # Проверяем, что sort_by_date был вызван с descending=False
        mock_sort.assert_called_once()
        call_kwargs = mock_sort.call_args.kwargs
        assert call_kwargs.get("descending") is False

    # ==================== ТЕСТ 7: CSV И XLSX ИСТОЧНИКИ ====================

    @patch("src.main.filter_by_state")
    @patch("src.main.load_data")
    @patch("builtins.input")
    def test_main_csv_source(
        self,
        mock_input: MagicMock,
        mock_load: MagicMock,
        mock_filter_state: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """🆕 Покрывает выбор CSV (choice=2)."""
        mock_input.side_effect = [
            "2",  # CSV
            "EXECUTED",
            "нет",
            "нет",
            "нет",
            "нет",
        ]
        mock_load.return_value = [SAMPLE_TRANSACTION]
        mock_filter_state.return_value = [SAMPLE_TRANSACTION]

        main()

        output = capsys.readouterr().out
        assert "Для обработки выбран CSV-файл" in output

    @patch("src.main.filter_by_state")
    @patch("src.main.load_data")
    @patch("builtins.input")
    def test_main_xlsx_source(
        self,
        mock_input: MagicMock,
        mock_load: MagicMock,
        mock_filter_state: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """🆕 Покрывает выбор XLSX (choice=3)."""
        mock_input.side_effect = [
            "3",  # XLSX
            "EXECUTED",
            "нет",
            "нет",
            "нет",
            "нет",
        ]
        mock_load.return_value = [SAMPLE_TRANSACTION]
        mock_filter_state.return_value = [SAMPLE_TRANSACTION]

        main()

        output = capsys.readouterr().out
        assert "Для обработки выбран XLSX-файл" in output
