import random
from typing import Dict, Generator, List


def filter_by_currency(transactions: List[Dict], currency: str) -> Generator:
    """
    Фильтрация транзакций по валюте.

    :param transactions: список транзакций
    :param currency: валюта, по которой фильтруем
    :yield: транзакция, если её валюта совпадает с переданной
    """
    for transaction in transactions:
        if transaction.get('currency') == currency:
            yield transaction


def transaction_descriptions(transactions: List[Dict]) -> Generator:
    """
    Генерация описаний транзакций.

    :param transactions: список транзакций
    :yield: описание транзакции или сообщение, если описание не указано
    """
    for transaction in transactions:
        yield transaction.get('description', 'Описание ситуации не указано')


def unique_card_number_generator(count: int) -> Generator:
    """
    Генератор уникальных номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    :param count: количество уникальных номеров карт для генерации
    :yield: номер карты в формате XXXX XXXX XXXX XXXX
    """
    generated_numbers: set[str] = set()

    while len(generated_numbers) < count:
        # Генерируем случайный номер карты
        num = random.randint(0, 9999999999999999)  # 16-значное число
        formatted_number = f"{num:016d}"
        card_number = (f"{formatted_number[:4]} {formatted_number[4:8]}"
                       f" {formatted_number[8:12]} {formatted_number[12:]}")

        # Добавляем номер в множество, чтобы избежать дубликатов
        if card_number not in generated_numbers:
            generated_numbers.add(card_number)
            yield card_number


# Пример использования генератора уникальных номеров карт
print("Уникальные номера карт:")
for card_number in unique_card_number_generator(10):
    print(card_number)

# Пример использования фильтрации транзакций
transactions = [
    {'amount': 100, 'currency': 'USD', 'description': 'Покупка'},
    {'amount': 50, 'currency': 'EUR', 'description': 'Оплата'},
    {'amount': 200, 'currency': 'USD', 'description': 'Перевод'},
]

print("\nТранзакции в USD:")
for txn in filter_by_currency(transactions, 'USD'):
    print(txn)

# Пример использования генератора описаний транзакций
print("\nОписания транзакций:")
for desc in transaction_descriptions(transactions):
    print(desc)
