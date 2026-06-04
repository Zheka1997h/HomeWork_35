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
def test_transaction_descriptions(transactions: List, expected:List[str]) -> None:
    """
    Тестирует функцию transaction_descriptions для правильного извлечения описаний транзакций.

    Args:
        transactions (List[Dict]): Список транзакций.
        expected (List[str]): Ожидаемый список описаний транзакций.
    """
    result = list(transaction_descriptions(transactions))
    assert result == expected


# Тесты для функции card_number_generator
@pytest.mark.parametrize("count", [1, 5, 10])
def test_card_number_generator(count: int) -> None:
    """
    Тестирует функцию card_number_generator для генерации указанного количества номеров карт.

    Args:
        count (int): Количество номеров карт для генерации.
    """
    cards = card_number_generator(count)
    assert len(cards) == count
    assert all(isinstance(card, str) and len(card) == 19 for card in cards)

    # Проверяем уникальность номеров
    assert len(set(cards)) == count


# Тесты для функции card_number_generator на исключения
@pytest.mark.parametrize(
    "count, start, stop, expected_exception",
    [
        (-1, 0, 9999999999999999, ValueError),  # отрицательное значение count
        (1, 10, 5, ValueError),  # stop меньше start
    ],
)
def test_card_number_generator_exceptions(count: int, start: int, stop: int, expected_exception):
    """
    Тестирует функцию card_number_generator на генерацию исключений при неверных параметрах.

    Args:
        count (int): Количество номеров карт для генерации.
        start (int): Начальный диапазон для генерации номеров.
        stop (int): Конечный диапазон для генерации номеров.
        expected_exception (Exception): Ожидаемое исключение.
    """
    with pytest.raises(expected_exception):
        card_number_generator(count, start, stop)


# Тесты для функции card_number_generator с полным покрытием
@pytest.mark.parametrize(
    "count, start, stop",
    [
        (5, 0, 9999999999999999),
        (5, 1000000000000000, 9999999999999999),
    ],
)
def test_card_number_generator_full_coverage(count: int, start: int, stop: int) -> None:
    """
    Тестирует функцию card_number_generator с полным покрытием диапазона номеров.

    Args:
        count (int): Количество номеров карт для генерации.
        start (int): Начальный диапазон для генерации номеров.
        stop (int): Конечный диапазон для генерации номеров.
    """
    cards = card_number_generator(count, start, stop)
    assert len(cards) == count
    assert all(isinstance(card, str) and len(card) == 19 for card in cards)

    # Проверяем уникальность номеров
    assert len(set(cards)) == count

    # Проверяем, что номера карт в правильном диапазоне
    for card in cards:
        # Удаляем пробелы и преобразуем в число
        card_number = int(card.replace(" ", ""))
        assert start <= card_number <= stop

    # Печатаем сгенерированные номера (для проверки)
    print("Сгенерированные номера карт:")
    for card in cards:
        print(card)
