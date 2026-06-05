from itertools import islice
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
        transactions = [
             {'operationAmount': {'currency': {'code': 'USD'}}},
        {'operationAmount': {'currency': {'code': 'RUB'}}
        ]
        list(filter_by_currency(transactions, 'USD'))
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
        transactions = [{'description': 'Покупка в магазине'}, {}]
        list(transaction_descriptions(transactions))
        ['Покупка в магазине', 'Описание ситуации не указано']
    """
    for transaction in transactions:
        yield transaction.get("description", "Описание ситуации не указано")


def card_number_generator(start: str, stop: str) -> Generator[str, None, None]:
    """
    Генерирует номера банковских карт в заданном диапазоне.

    Номера карт форматируются в виде "XXXX XXXX XXXX XXXX" (16 цифр с пробелами каждые 4 цифры).

    Args:
        start (str): Начальный номер карты в формате "XXXX XXXX XXXX XXXX".
            Может содержать пробелы, которые будут удалены перед обработкой.
        stop (str): Конечный номер карты в формате "XXXX XXXX XXXX XXXX".
            Может содержать пробелы, которые будут удалены перед обработкой.

    Yields:
        str: Отформатированный номер карты в виде "XXXX XXXX XXXX XXXX".

    Raises:
        ValueError: Если start или stop не могут быть преобразованы в целые числа
            после удаления пробелов (некорректный формат номера карты).

    Examples:
        >>> gen = card_number_generator("0000 0000 0000 0001", "0000 0000 0000 0003")
        >>> list(gen)
        ['0000 0000 0000 0001', '0000 0000 0000 0002']

        >>> next(card_number_generator("1234 5678 9012 3456", "1234 5678 9012 3457"))
        '1234 5678 9012 3456'
    """
    try:
        # Преобразуем начальное и конечное значение в числа
        start_num = int(start.replace(" ", ""))
        stop_num = int(stop.replace(" ", ""))
    except ValueError:
        raise ValueError("Некорректный формат номера карты")

    # Генерируем все возможные номера карт в заданном диапазоне
    for num in range(start_num, stop_num):
        # Преобразуем число в строку с ведущими нулями
        card_number = f"{num:016}"
        # Форматируем строку в нужный формат "XXXX XXXX XXXX XXXX"
        formatted_card_number = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:]}"
        yield formatted_card_number


# Пример использования
start_card = "0000 0000 0000 0001"
stop_card = "0000 0000 0000 0010"
for card in islice(card_number_generator(start_card, stop_card), 10):
    print(card)
