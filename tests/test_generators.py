from typing import Dict, List

import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


# Фикстура для транзакций
@pytest.fixture
def transactions() -> List[Dict]:
    """
    Создает фикстуру списка транзакций.

    Returns:
        List[Dict]: Список транзакций со словарями, содержащими информацию о валюте и описании.
    """
    return [
        {"operationAmount": {"currency": {"code": "USD"}}},
        {"operationAmount": {"currency": {"code": "RUB"}}},
        {"description": "Покупка в магазине"},
        {},
    ]


# Тесты для функции filter_by_currency
@pytest.mark.parametrize(
    "currency, expected",
    [
        ("USD", [{"operationAmount": {"currency": {"code": "USD"}}}]),
        ("RUB", [{"operationAmount": {"currency": {"code": "RUB"}}}]),
        ("EUR", []),
    ],
)
def test_filter_by_currency(transactions: List, currency: str, expected: List) -> None:
    """
    Тестирует функцию filter_by_currency, чтобы убедиться, что она правильно фильтрует транзакции по валюте.

    Args:
        transactions (List[Dict]): Список транзакций.
        currency (str): Код валюты для фильтрации.
        expected (List[Dict]): Ожидаемый результат фильтрации.
    """
    result = list(filter_by_currency(transactions, currency))
    assert result == expected


# Тесты для функции transaction_descriptions
@pytest.mark.parametrize(
    "expected",
    [
        [
            "Описание ситуации не указано",
            "Описание ситуации не указано",
            "Покупка в магазине",
            "Описание ситуации не указано",
        ]
    ],
)
def test_transaction_descriptions(transactions: List, expected: List[str]) -> None:
    """
    Тестирует функцию transaction_descriptions для правильного извлечения описаний транзакций.

    Args:
        transactions (List[Dict]): Список транзакций.
        expected (List[str]): Ожидаемый список описаний транзакций.
    """
    result = list(transaction_descriptions(transactions))
    assert result == expected


# Фикстура для установки начального и конечного значений


# Тестируем генерацию номеров карт

# Ожидаемый результат
expected_results = ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003", "0000 0000 0000 0004"]


# Создаем тест
@pytest.mark.parametrize("start, stop, expected", [(1, 5, expected_results)])
def test_card_number_generator(start: int, stop: int, expected: List[int]) -> None:
    # Запускаем генератор
    generator = card_number_generator(start, stop)

    # Проверяем, что сгенерированные номера карт совпадают с ожидаемыми
    assert list(generator) == expected


# Функция, которая может вызвать исключение
# Это пример, так что замени его на свою функцию


def check_card_number(card_number) -> None:
    if not isinstance(card_number, str):
        raise ValueError("Некорректный формат номера карты")
    # ... другой код


# Тестовая функция


def test_check_card_number_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Некорректный формат номера карты"):
        check_card_number(1234567890123456)  # Передаем некорректный формат, например, число вместо строки
