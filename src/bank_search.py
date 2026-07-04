import re
from collections import Counter


def process_bank_search(data: list[dict], search: str) -> list[dict]:
    """
    Ищет банковские операции по строке в поле description.

    Функция принимает список словарей с данными о банковских операциях
    и строку поиска. Возвращает список словарей, у которых в описании
    содержится искомая строка. Для поиска используется библиотека re
    (регулярные выражения). Поиск регистронезависимый, спецсимволы
    регулярных выражений экранируются.

    :param data: Список словарей с данными о банковских операциях.
    :param search: Строка для поиска в описании операций.
    :return: Список словарей с операциями, содержащими искомую строку.
    """
    if not search:
        return list(data)

    pattern = re.compile(re.escape(search), re.IGNORECASE)
    return [operation for operation in data if pattern.search(operation.get("description", ""))]


def process_bank_operations(data: list[dict], categories: list[str]) -> dict[str, int]:
    """
    Подсчитывает количество банковских операций по заданным категориям.

    Функция принимает список словарей с данными о банковских операциях
    и список категорий. Возвращает словарь, где ключи — названия
    категорий, а значения — количество операций в каждой категории.
    Категория определяется по полю description. Для подсчёта
    используется collections.Counter.

    :param data: Список словарей с данными о банковских операциях.
    :param categories: Список категорий для подсчёта.
    :return: Словарь вида {категория: количество}.
    """
    descriptions = [operation.get("description", "") for operation in data]
    counter = Counter(descriptions)
    return {category: counter.get(category, 0) for category in categories}
