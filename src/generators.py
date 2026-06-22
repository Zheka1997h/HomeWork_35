from typing import Any, Dict, Generator, List


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Generator[Dict[str, Any], None, None]:
    """Фильтрация транзакций по валюте.

    Args:
        transactions: Список транзакций. Каждая транзакция — словарь,
            который может содержать вложенную структуру с информацией о валюте
            в поле 'operationAmount' -> 'currency' -> 'code'.
        currency: Валюта, по которой выполняется фильтрация (например, 'USD', 'RUB').

    Yields:
        Транзакция (словарь), если код валюты совпадает с переданным параметром.

    Example:
        >>> transactions = [
        ...     {'operationAmount': {'currency': {'code': 'USD'}}},
        ...     {'operationAmount': {'currency': {'code': 'RUB'}}}
        ... ]
        >>> list(filter_by_currency(transactions, 'USD'))
        [{'operationAmount': {'currency': {'code': 'USD'}}}]
    """
    for transaction in transactions:
        if transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency:
            yield transaction


def transaction_descriptions(
    transactions: List[Dict[str, Any]],
) -> Generator[str, None, None]:
    """Генерация описаний транзакций.

    Args:
        transactions: Список транзакций. Каждая транзакция — словарь,
            который может содержать поле 'description'.

    Yields:
        Описание транзакции из поля 'description'. Если поле отсутствует,
        возвращается строка 'Описание ситуации не указано'.

    Example:
        >>> transactions = [{'description': 'Покупка в магазине'}, {}]
        >>> list(transaction_descriptions(transactions))
        ['Покупка в магазине', 'Описание ситуации не указано']
    """
    for transaction in transactions:
        yield transaction.get("description", "Описание ситуации не указано")


def card_number_generator(start: int, stop: int) -> Generator[str, None, None]:
    """Генератор номеров банковских карт в заданном диапазоне.

    Args:
        start: Начальное значение диапазона (включительно).
        stop: Конечное значение диапазона (не включительно).

    Yields:
        Номер карты в формате "XXXX XXXX XXXX XXXX".

    Example:
        >>> list(card_number_generator(1, 3))
        ['0000 0000 0000 0001', '0000 0000 0000 0002']
    """
    for num in range(start, stop):
        card_number = f"{num:016d}"
        formatted_card_number = f"{card_number[:4]} {card_number[4:8]} " f"{card_number[8:12]} {card_number[12:]}"
        yield formatted_card_number


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
