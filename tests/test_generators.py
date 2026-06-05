from itertools import islice
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


@pytest.fixture
def card_range():
    start_card = "0000 0000 0000 0001"
    stop_card = "0000 0000 0000 0010"
    return start_card, stop_card


# Параметризированный тест для проверки генерации номеров карт


@pytest.mark.parametrize(
    "start, stop, expected",
    [
        (
            "0000 0000 0000 0001",
            "0000 0000 0000 0010",
            [
                "0000 0000 0000 0001",
                "0000 0000 0000 0002",
                "0000 0000 0000 0003",
                "0000 0000 0000 0004",
                "0000 0000 0000 0005",
                "0000 0000 0000 0006",
                "0000 0000 0000 0007",
                "0000 0000 0000 0008",
                "0000 0000 0000 0009",
            ],
        )
    ],
)
def test_card_number_generator(card_range: tuple[str, str], start: str, stop: str, expected: List[str]) -> None:
    # Используем фикстуру card_range для получения начального и конечного значений
    start, stop = card_range
    result = list(islice(card_number_generator(start, stop), 9))
    assert result == expected
