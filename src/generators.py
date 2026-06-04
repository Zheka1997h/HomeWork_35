import random
from typing import Dict, Generator, List


def filter_by_currency(transactions: List[Dict], currency: str) -> Generator:
    """
    Фильтрация транзакций по валюте.

    Args:
        transactions (List[Dict]): Список транзакций. Каждая транзакция — словарь,
            который может содержать вложенную структуру с информацией о валюте
            в поле 'operationAmount' -> 'currency' -> 'code'.
        currency (str): Валюта, по которой выполняется фильтрация (например, 'USD', 'RUB').

    Yields:
        Dict: Транзакция (словарь), если код валюты в транзакции совпадает с переданным параметром.

    Example:
        >>> transactions = [
        ...     {'operationAmount': {'currency': {'code': 'USD'}}},
        ...     {'operationAmount': {'currency': {'code': 'RUB'}}
        ... ]
        >>> list(filter_by_currency(transactions, 'USD'))
        [{'operationAmount': {'currency': {'code': 'USD'}}]
    """
    for transaction in transactions:
        # Извлекаем код валюты из вложенной структуры
        if transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency:
            yield transaction


def transaction_descriptions(transactions: List[Dict]) -> Generator:
    """
    Генерация описаний транзакций.

    Args:
        transactions (List[Dict]): Список транзакций. Каждая транзакция — словарь,
            который может содержать поле 'description'.

    Yields:
        str: Описание транзакции из поля 'description', если оно есть.
            Если поле отсутствует или пусто, возвращается строка
            'Описание ситуации не указано'.

    Example:
        >>> transactions = [{'description': 'Покупка в магазине'}, {}]
        >>> list(transaction_descriptions(transactions))
        ['Покупка в магазине', 'Описание ситуации не указано']
    """
    for transaction in transactions:
        yield transaction.get("description", "Описание ситуации не указано")


def card_number_generator(count: int, start: int = 0, stop: int = 9999999999999999) -> set:
    """
    Генерирует уникальные номера банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        count (int): Количество уникальных номеров карт для генерации.
        start (int, optional): Начальное значение диапазона генерации чисел.
            По умолчанию 0.
        stop (int, optional): Конечное значение диапазона генерации чисел
            (включительно). По умолчанию 9999999999999999
            (16‑значное максимальное число).

    Returns:
        set: Множество строк с отформатированными номерами карт.
            Каждый номер имеет вид 'XXXX XXXX XXXX XXXX'.

    Raises:
        ValueError: Если count отрицательный или если диапазон [start, stop]
            не позволяет сгенерировать требуемое количество уникальных номеров.

    Example:
        >>> cards = card_number_generator(2)
        >>> len(cards)
        2
        >>> all(isinstance(card, str) and len(card) == 19 for card in cards)
        True
    """
    if count < 0:
        raise ValueError("Параметр count не может быть отрицательным")
    if stop < start:
        raise ValueError("Параметр stop должен быть больше или равен start")

    generated_numbers: set[str] = set()
    while len(generated_numbers) < count:
        # Генерируем случайный номер карты в заданном диапазоне
        num = random.randint(start, stop)  # число в диапазоне от start до stop
        formatted_number = f"{num:016d}"
        card_number = (
            f"{formatted_number[:4]} {formatted_number[4:8]} " f"{formatted_number[8:12]} {formatted_number[12:]}"
        )
        generated_numbers.add(card_number)  # Добавляем номер в набор

    return generated_numbers  # Возвращаем сгенерированные номера
