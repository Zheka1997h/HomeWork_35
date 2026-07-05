# -*- coding: utf-8 -*-
import re
from collections import Counter

from src.decorators import log


@log()
def process_bank_search(data: list[dict], search: str) -> list[dict]:
    """Ищет банковские операции по строке в поле description."""
    if not search:
        return list(data)

    pattern = re.compile(re.escape(search), re.IGNORECASE)
    return [operation for operation in data if pattern.search(operation.get("description", ""))]


@log()
def process_bank_operations(data: list[dict], categories: list[str]) -> dict[str, int]:
    """Подсчитывает количество банковских операций по заданным категориям."""
    descriptions = [operation.get("description", "") for operation in data]
    counter = Counter(descriptions)
    return {category: counter.get(category, 0) for category in categories}
