# Виджет банковских операций клиента

## Описание

Этот проект представляет собой совокупность модулей для обработки банковских операций клиента. Он позволяет фильтровать и сортировать операции на основе их состояния и даты.

## Установка
1.  Клонируйте репозиторий:
    ```bash
    git clone github.com/Zheka1997h/HomeWork_35/pull/1#issue-4534818177
    ```
2.  Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Установите необходимые библиотеки:
    ```bash
    pip install -r requirements.txt
    ```

## Использование

### Функции

#### `filter_by_state(transactions: List[Dict], state: str = 'EXECUTED') -> List[Dict]`

Фильтрует список операций по состоянию.

- **transactions**: Список словарей с данными о банковских операциях.
- **state**: Значение для фильтрации по ключу 'state'. По умолчанию 'EXECUTED'.

#### `transaction_descriptions(transactions: List[Dict]) -> Generator`
"""
Генерация описаний транзакций.
:param transactions: список транзакций
:yield: описание транзакции или сообщение, если описание не указано
"""
#### `transaction_descriptions(transactions: List[Dict]) -> Generator`
"""
Генератор уникальных номеров банковских карт в формате XXXX XXXX XXXX XXXX.
:param count: количество уникальных номеров карт для генерации
 :yield: номер карты в формате XXXX XXXX XXXX XXXX
 """

## Тестирование

Для тестирования модулей `masks.py`, `proccessing.py`, widget.py и generators.py выполните следующие шаги:

1. Убедитесь, что у вас установлен Python и все зависимости проекта.

2. Перейдите в корневую директорию проекта.

3. Запустите тесты для модулей:
    
    ```bash
    python -m pytest tests/test_masks.py
    ```
    
    ```bash
    python -m pytest tests/test_proccessing.py
    ```

     ```bash
    python -m pytest tests/test_widget.py
    ```
   ```bash
    python -m pytest tests/test_generators.py
    ```
    ```bash
    python -m pytest tests/test_decorators.py
    ```

Это запустит тесты для соответствующих модулей и выведет результаты в консоль.
   
## Структура проекта
-   `masks`: Скрипт шифрования карты
-   `src/`: Вспомогательные функции для обработки текста.
-   `masks.py`: Скрипт реализует маскрировку карт и транзакций по ним.
-   `widget.py`: Скрипт для визуализации отображения номера карты.
-   `proccessing.py`: Скрипт реализует обработку и сортировку транзакций.
-   `generators.py`: Скрипт реализует описание и фильтрацию транзакций по картам.
-   `decorators.py`: Скрипт декоратор регистрирующий детали выполнения функций.
-    test_masks - модкль для тестрирования маскировки карт и транзакций
-    test_proccessings - модуль для тестирования транзакций по картам
-    test_widget.py - модуль для тестирования данных по картам
-    test_generators.py - модуль для тестрирования генераторов и функций
-    test_decorators.pu - модуль для тестирования декоратора функции
-   `requirements.txt`: Список зависимостей.

## Примеры использования

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


## Лицензия
Этот проект распространяется под лицензией MIT.
