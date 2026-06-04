from typing import Any, Dict, List

import pytest

from src.generators import filter_by_currency, transaction_descriptions, unique_card_number_generator

# Фикстура для транзакций


@pytest.fixture
def transactions() -> List[Dict[str, Any]]:
    """
    Создает фикстуру транзакций для тестов.

    :return: Список транзакций.
    """
    return [
        {"amount": 100, "currency": "USD", "description": "Покупка"},
        {"amount": 50, "currency": "EUR", "description": "Оплата"},
        {"amount": 200, "currency": "USD", "description": "Перевод"},
        {"amount": 75, "currency": "EUR"},  # Без описания
    ]


# Тест для filter_by_currency с обработкой исключений


def test_filter_by_currency(transactions: List[Dict[str, Any]]) -> None:
    """
    Тестирует функцию filter_by_currency, проверяя, что она правильно фильтрует транзакции по валюте.

    :param transactions: Список транзакций для фильтрации.
    """
    try:
        usd_transactions = list(filter_by_currency(transactions, "USD"))
        assert len(usd_transactions) == 2
        assert all(txn["currency"] == "USD" for txn in usd_transactions)

        eur_transactions = list(filter_by_currency(transactions, "EUR"))
        assert len(eur_transactions) == 2
        assert all(txn["currency"] == "EUR" for txn in eur_transactions)
    except Exception as e:
        raise ValueError(f"Ошибка при фильтрации транзакций: {e}")


# Тест для transaction_descriptions с обработкой исключений


def test_transaction_descriptions(transactions: List[Dict[str, Any]]) -> None:
    """
    Тестирует функцию transaction_descriptions, проверяя, что она возвращает правильные описания транзакций.

    :param transactions: Список транзакций для получения описаний.
    """
    try:
        descriptions = list(transaction_descriptions(transactions))
        assert len(descriptions) == 4
        assert descriptions[0] == "Покупка"
        assert descriptions[1] == "Оплата"
        assert descriptions[2] == "Перевод"
        assert descriptions[3] == "Описание ситуации не указано"  # Без описания
    except Exception as e:
        raise ValueError(f"Ошибка при получении описаний транзакций: {e}")


# Параметризованный тест для unique_card_number_generator с обработкой исключений


@pytest.mark.parametrize(
    "count, expected_count",
    [
        (5, 5),
        (10, 10),
        (15, 15),
    ],
)
def test_unique_card_number_generator(count: int, expected_count: int, transactions: List[Dict[str, Any]]) -> None:
    """
    Тестирует функцию unique_card_number_generator, проверяя, что она генерирует указанное количество
    уникальных номеров карт.
    :param count: Количество номеров карт для генерации.
    :param expected_count: Ожидаемое количество уникальных номеров.
    :param transactions: Список транзакций (не используется в данном тесте, но передается).
    """
    try:
        card_numbers = list(unique_card_number_generator(count))
        assert len(card_numbers) == expected_count
        assert len(set(card_numbers)) == expected_count  # Все номера должны быть уникальными
    except Exception as e:
        raise ValueError(f"Ошибка при генерации уникальных номеров карт: {e}")
