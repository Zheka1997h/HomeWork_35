# -*- coding: utf-8 -*-
from typing import Dict, List

from src.decorators import log


@log()
def filter_by_state(transactions: List[Dict], state: str = "EXECUTED") -> List[Dict]:
    """Фильтрует список словарей по значению ключа 'state'."""
    return [transaction for transaction in transactions if transaction.get("state") == state]


@log()
def sort_by_date(transactions: List[Dict], descending: bool = True) -> List[Dict]:
    """Сортирует список словарей по дате."""
    return sorted(transactions, key=lambda x: x["date"], reverse=descending)
