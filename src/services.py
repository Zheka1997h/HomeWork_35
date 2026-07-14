import logging
import re
from datetime import datetime
from functools import reduce
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def get_top_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
    """Анализ выгодности категорий повышенного кешбэка."""
    filtered = list(
        filter(
            lambda x: datetime.strptime(x["Дата операции"], "%d.%m.%Y").year == year
            and datetime.strptime(x["Дата операции"], "%d.%m.%Y").month == month,
            data,
        )
    )

    cashback_by_cat = {}
    for row in filtered:
        cat = row.get("Категория", "Другое")
        cb = float(row.get("Кэшбэк", 0) or 0)
        cashback_by_cat[cat] = cashback_by_cat.get(cat, 0) + cb

    sorted_cats = sorted(cashback_by_cat.items(), key=lambda x: x[1], reverse=True)
    top_n = max(3, len(sorted_cats))

    return dict(sorted_cats[:top_n])


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Расчет суммы для Инвесткопилки."""
    target_year, target_month = map(int, month.split("-"))

    filtered = list(
        filter(
            lambda x: datetime.strptime(x["Дата операции"], "%d.%m.%Y").year == target_year
            and datetime.strptime(x["Дата операции"], "%d.%m.%Y").month == target_month,
            transactions,
        )
    )

    def calc_rounding(amount):
        amount = abs(float(amount))
        if amount == 0:
            return 0
        rounded_up = ((int(amount) + limit - 1) // limit) * limit
        return rounded_up - int(amount)

    roundings = map(lambda x: calc_rounding(x.get("Сумма операции", 0) or 0), filtered)
    total_saved = reduce(lambda acc, val: acc + val, roundings, 0.0)

    return round(total_saved, 2)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Простой поиск по подстроке (нечувствителен к регистру)."""
    query_lower = query.lower()
    return list(
        filter(
            lambda x: query_lower in str(x.get("Описание", "")).lower()
            or query_lower in str(x.get("Категория", "")).lower(),
            transactions,
        )
    )


def search_by_phone(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Поиск транзакций с мобильными номерами в описании."""
    phone_pattern = re.compile(r"(?:\+7|8)[\s\-\(]*\d{3}[\s\-\)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}")
    return list(filter(lambda x: phone_pattern.search(str(x.get("Описание", ""))), transactions))


def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Поиск переводов физическим лицам."""
    name_pattern = re.compile(r"^[А-Яа-яЁё]+ [А-Яа-яЁё]\.$")

    return list(
        filter(
            lambda x: x.get("Категория") == "Переводы" and name_pattern.match(str(x.get("Описание", ""))), transactions
        )
    )
