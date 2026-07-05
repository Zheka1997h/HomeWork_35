# -*- coding: utf-8 -*-
from typing import Dict, List

import pytest

from src.proccessing import filter_by_state, sort_by_date


@pytest.fixture
def transactions() -> List[Dict]:
    """Возвращает список транзакций для тестирования.

    Returns:
        List[Dict]: Список транзакций, каждая из которых представлена словарем.
    """
    return [
        {"id": 1, "date": "2023-10-01", "state": "EXECUTED"},
        {"id": 2, "date": "2023-09-30", "state": "CANCELED"},
        {"id": 3, "date": "2023-10-02", "state": "EXECUTED"},
        {"id": 4, "date": "2023-09-29", "state": "PENDING"},
    ]


@pytest.mark.parametrize(
    "state, expected_ids", [("EXECUTED", [1, 3]), ("CANCELED", [2]), ("PENDING", [4]), ("NOT_EXISTING", [])]
)
def test_filter_by_state(transactions: List[Dict], state: str, expected_ids: List[int]) -> None:
    """Тестирует функцию filter_by_state, проверяя фильтрацию транзакций по состоянию.

    Args:
        transactions (List[Dict]): Список транзакций для фильтрации.
        state (str): Состояние, по которому фильтруются транзакции.
        expected_ids (List[int]): Ожидаемый список идентификаторов транзакций после фильтрации.
    """
    filtered = filter_by_state(transactions, state)
    assert len(filtered) == len(expected_ids)
    assert [t["id"] for t in filtered] == expected_ids


# Параметризованные тесты для sort_by_date
@pytest.mark.parametrize(
    "descending, expected_order", [(True, [3, 1, 2, 4]), (False, [4, 2, 1, 3])]  # По убыванию  # По возрастанию
)
def test_sort_by_date(transactions: List[Dict], descending: bool, expected_order: List[int]) -> None:
    """Тестирует функцию sort_by_date, проверяя сортировку транзакций по дате.

    Args:
        transactions (List[Dict]): Список транзакций для сортировки.
        descending (bool): Параметр, определяющий порядок сортировки (по убыванию или возрастанию).
        expected_order (List[int]): Ожидаемый порядок идентификаторов транзакций после сортировки.
    """
    sorted_transactions = sort_by_date(transactions, descending)
    assert [t["id"] for t in sorted_transactions] == expected_order
