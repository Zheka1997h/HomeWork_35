# -*- coding: utf-8 -*-
from typing import Any, Dict, Generator, List

from src.decorators import log


@log()
def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Generator[Dict[str, Any], None, None]:
    """Фильтрация транзакций по валюте."""
    for transaction in transactions:
        if transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency:
            yield transaction


@log()
def transaction_descriptions(
    transactions: List[Dict[str, Any]],
) -> Generator[str, None, None]:
    """Генерация описаний транзакций."""
    for transaction in transactions:
        yield transaction.get("description", "Описание ситуации не указано")


@log()
def card_number_generator(start: int, stop: int) -> Generator[str, None, None]:
    """Генератор номеров банковских карт в заданном диапазоне."""
    for num in range(start, stop):
        card_number = f"{num:016d}"
        formatted_card_number = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:]}"
        yield formatted_card_number


@log()
def check_card_number(card_number: Any) -> None:
    """Проверяет корректность формата номера карты.

    Номер карты должен быть строкой. Если передан другой тип —
    выбрасывается ValueError.

    Args:
        card_number: Номер карты (должен быть строкой).

    Raises:
        ValueError: Если номер карты не является строкой.
    """
    if not isinstance(card_number, str):
        raise ValueError("Некорректный формат номера карты")
