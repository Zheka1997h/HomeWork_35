# -*- coding: utf-8 -*-
from typing import Any, Dict, List

import pytest

from src.generators import card_number_generator, check_card_number, filter_by_currency, transaction_descriptions


@pytest.fixture
def transactions() -> List[Dict[str, Any]]:
    """Создает фикстуру списка транзакций."""
    return [
        {"operationAmount": {"currency": {"code": "USD"}}},
        {"operationAmount": {"currency": {"code": "RUB"}}},
        {"description": "Покупка в магазине"},
        {},
    ]


@pytest.mark.parametrize(
    "currency, expected",
    [
        ("USD", [{"operationAmount": {"currency": {"code": "USD"}}}]),
        ("RUB", [{"operationAmount": {"currency": {"code": "RUB"}}}]),
        ("EUR", []),
    ],
)
def test_filter_by_currency(transactions: List[Dict[str, Any]], currency: str, expected: List[Dict[str, Any]]) -> None:
    """Тестирует функцию filter_by_currency."""
    result = list(filter_by_currency(transactions, currency))
    assert result == expected


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
def test_transaction_descriptions(transactions: List[Dict[str, Any]], expected: List[str]) -> None:
    """Тестирует функцию transaction_descriptions."""
    result = list(transaction_descriptions(transactions))
    assert result == expected


@pytest.mark.parametrize(
    "start, stop, expected",
    [
        (
            1,
            5,
            [
                "0000 0000 0000 0001",
                "0000 0000 0000 0002",
                "0000 0000 0000 0003",
                "0000 0000 0000 0004",
            ],
        ),
    ],
)
def test_card_number_generator(start: int, stop: int, expected: List[str]) -> None:
    """Тестирует генерацию номеров карт."""
    generator = card_number_generator(start, stop)
    assert list(generator) == expected


def test_check_card_number_raises_value_error() -> None:
    """Тест: при передаче числа вместо строки выбрасывается ValueError."""
    with pytest.raises(ValueError, match="Некорректный формат номера карты"):
        check_card_number(1234567890123456)  # int вместо str


def test_check_card_number_accepts_string() -> None:
    """Тест: строка принимается без ошибок."""
    check_card_number("1234 5678 9012 3456")  # Не должно выбрасывать исключение
