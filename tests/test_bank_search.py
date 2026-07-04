"""Тесты для модуля bank_search."""

from typing import Any

import pytest

from src.bank_search import process_bank_operations, process_bank_search


@pytest.fixture
def sample_data() -> list[dict[str, Any]]:
    """Возвращает тестовые данные банковских операций."""
    return [
        {
            "id": 1,
            "description": "Перевод организации",
            "state": "EXECUTED",
            "date": "2019-07-03T18:35:29.512364",
            "operationAmount": {
                "amount": "8200.00",
                "currency": {"name": "RUB", "code": "RUB"},
            },
        },
        {
            "id": 2,
            "description": "Открытие вклада",
            "state": "EXECUTED",
            "date": "2019-12-08T00:00:00.000000",
            "operationAmount": {
                "amount": "40542.00",
                "currency": {"name": "руб.", "code": "RUB"},
            },
        },
        {
            "id": 3,
            "description": "Перевод с карты на карту",
            "state": "CANCELED",
            "date": "2019-11-12T00:00:00.000000",
            "operationAmount": {
                "amount": "130.00",
                "currency": {"name": "USD", "code": "USD"},
            },
        },
    ]


class TestProcessBankSearch:
    """Тесты функции process_bank_search."""

    def test_search_found(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест поиска с найденными результатами."""
        result: list[dict[str, Any]] = process_bank_search(sample_data, "Перевод")
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 3

    def test_search_not_found(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест поиска без результатов."""
        result: list[dict[str, Any]] = process_bank_search(sample_data, "несуществующее")
        assert result == []

    def test_search_empty_list(self) -> None:
        """Тест поиска в пустом списке."""
        result: list[dict[str, Any]] = process_bank_search([], "Перевод")
        assert result == []

    def test_search_empty_string(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест поиска с пустой строкой."""
        result: list[dict[str, Any]] = process_bank_search(sample_data, "")
        assert len(result) == 3

    def test_search_case_insensitive(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест регистронезависимого поиска."""
        result: list[dict[str, Any]] = process_bank_search(sample_data, "перевод")
        assert len(result) == 2

    def test_search_special_chars(self) -> None:
        """Тест поиска со специальными символами."""
        data: list[dict[str, Any]] = [{"id": 4, "description": "Операция с точкой."}]
        result: list[dict[str, Any]] = process_bank_search(data, "точкой.")
        assert len(result) == 1

    def test_search_regex_chars_escaped(self) -> None:
        """Тест экранирования regex-символов."""
        data: list[dict[str, Any]] = [{"id": 4, "description": "Операция с [скобками]"}]
        result: list[dict[str, Any]] = process_bank_search(data, "[скобками]")
        assert len(result) == 1

    def test_search_missing_description(self) -> None:
        """Тест поиска при отсутствии поля description."""
        data: list[dict[str, Any]] = [{"id": 1}, {"id": 2, "description": "Перевод"}]
        result: list[dict[str, Any]] = process_bank_search(data, "Перевод")
        assert len(result) == 1


class TestProcessBankOperations:
    """Тесты функции process_bank_operations."""

    def test_count_categories(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест подсчёта категорий."""
        categories: list[str] = ["Перевод организации", "Открытие вклада"]
        result: dict[str, int] = process_bank_operations(sample_data, categories)
        assert result == {"Перевод организации": 1, "Открытие вклада": 1}

    def test_count_missing_category(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест подсчёта с отсутствующей категорией."""
        categories: list[str] = ["Перевод организации", "Несуществующая"]
        result: dict[str, int] = process_bank_operations(sample_data, categories)
        assert result == {"Перевод организации": 1, "Несуществующая": 0}

    def test_count_empty_data(self) -> None:
        """Тест подсчёта на пустых данных."""
        result: dict[str, int] = process_bank_operations([], ["Перевод организации"])
        assert result == {"Перевод организации": 0}

    def test_count_empty_categories(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест подсчёта с пустым списком категорий."""
        result: dict[str, int] = process_bank_operations(sample_data, [])
        assert result == {}

    def test_count_multiple_same(self, sample_data: list[dict[str, Any]]) -> None:
        """Тест подсчёта нескольких одинаковых категорий."""
        categories: list[str] = [
            "Перевод организации",
            "Перевод с карты на карту",
        ]
        result: dict[str, int] = process_bank_operations(sample_data, categories)
        assert result == {
            "Перевод организации": 1,
            "Перевод с карты на карту": 1,
        }

    def test_count_missing_description(self) -> None:
        """Тест подсчёта при отсутствии поля description."""
        data: list[dict[str, Any]] = [{"id": 1}, {"id": 2, "description": "Перевод"}]
        result: dict[str, int] = process_bank_operations(data, ["Перевод"])
        assert result == {"Перевод": 1}
