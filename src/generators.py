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


def card_number_generator(start: int, stop: int) -> Generator[str, None, None]:

    try:
        # Преобразуем начальное и конечное значение в числа
        start_num = start
        stop_num = stop
    except ValueError:
        raise ValueError("Некорректный формат номера карты")

    # Генерируем все возможные номера карт в заданном диапазоне
    for num in range(start_num, stop_num):
        # Преобразуем число в строку с ведущими нулями
        card_number = f"{num:016}"
        # Форматируем строку в нужный формат "XXXX XXXX XXXX XXXX"
        formatted_card_number = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:]}"

        yield formatted_card_number


generator = card_number_generator(1, 5)

for card_number in generator:
    print(card_number)
