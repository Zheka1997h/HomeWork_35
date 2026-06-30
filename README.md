# Виджет банковских операций клиента

## 📋 Описание

Проект представляет собой набор модулей для обработки банковских операций клиента. 
Основные возможности:

- 🔐 Маскировка номеров карт и счетов
- 🔍 Фильтрация и сортировка транзакций
- 💱 Конвертация валют в рубли через внешний API
- 📄 Чтение данных из JSON-файла
- 📊 Генерация описаний транзакций и номеров карт
- 📝 Логирование вызовов функций через декоратор
- 📄  Чтение данных из Csv-файла.

## 🛠 Технологии

- **Python 3.11+**
- **requests** — работа с внешним API
- **python-dotenv** — управление переменными окружения
- **pytest** — тестирование
- **flake8** — проверка стиля кода (PEP 8)
- **mypy** — статическая проверка типов
- **isort** — сортировка импортов

## 📦 Установка

### 1. Клонирование репозитория

```bash
it clone https://github.com/Zheka1997h/HomeWork_35.git
cd HomeWork_35
```

### 2. Создание и активация виртуального окружения Windows:

```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```

```bash
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
```bash
HomeWork_35/
├── data/
│   ├── transactions.csv
│   ├── transactions_excel.xlsx
│   └── operations.json          # Данные о банковских операциях
│
│   ├── logs/                    # Логирование (вывод информации в файл)
│   ├── masks.log
│   └── utils.log
│    
├── src/
│   ├── __init__.py
│   ├── masks.py                 # Маскировка номеров карт и счетов
│   ├── widget.py                # Отображение информации о картах
│   ├── processing.py            # Фильтрация и сортировка транзакций
│   ├── generators.py            # Генераторы описаний и номеров карт
│   ├── decorators.py            # Декоратор для логирования
│   ├── transactions.py          # Чтение Сsv и Ecxel файла черз csv и pandas
│   ├── utils.py                 # Чтение JSON-файлов
│   └── external_api.py          # Конвертация валют через API
├── tests/
│   ├── __init__.py
│   ├── test_masks.py
│   ├── test_widget.py
│   ├── test_processing.py
│   ├── test_generators.py
│   ├── test_decorators.py
│   ├── test_transactions.py
│   ├── test_utils.py
│   └── test_external_api.py
├── .env                         # Переменные окружения (НЕ в Git)
├── .env.example                 # Шаблон переменных окружения
├── .flake8                      # Конфигурация flake8
├── mypy.ini                     # Конфигурация mypy
├── requirements.txt
└── README.md
```

### 1. Чтение данных из JSON-файла

```bash
from src.utils import read_json_file

# Чтение списка транзакций
transactions = read_json_file("data/operations.json")
print(transactions)
```

### 2. Маскировка номера карты

```bash
from src.masks import get_mask_card_number

print(get_mask_card_number("1234567890123456"))
# Вывод: 1234 56** **** 3456
```

### 3. Фильтрация транзакций по статусу

```bash
from src.processing import filter_by_state

transactions = [
    {"id": 1, "state": "EXECUTED", "date": "2023-01-01"},
    {"id": 2, "state": "CANCELED", "date": "2023-01-02"},
]

executed = filter_by_state(transactions, state="EXECUTED")
print(executed)
```
### 4. Сортировка транзакций по дате

```bash
from src.processing import sort_by_date

sorted_transactions = sort_by_date(transactions, reverse=True)
```

### 5. Конвертация валюты в рубли

```bash
from src.external_api import convert_transaction_to_rub

transaction = {
    "operationAmount": {
        "amount": "100.00",
        "currency": {"code": "USD"}
    }
}

amount_in_rub = convert_transaction_to_rub(transaction)
print(f"Сумма в рублях: {amount_in_rub}")
```

### 6. Генерация номеров карт

```bash
from src.generators import card_number_generator

# Генерация номеров карт в диапазоне от 1 до 5
for card in card_number_generator(1, 5):
    print(card)
# Вывод:
# 0000 0000 0000 0001
# 0000 0000 0000 0002
# ...
```

### 7. Генерация описаний транзакций

```bash
from src.generators import transaction_descriptions

transactions = [
    {"description": "Покупка в магазине"},
    {},
]

for desc in transaction_descriptions(transactions):
    print(desc)
# Вывод:
# Покупка в магазине
# Описание ситуации не указано
```

### 8. Логирование вызовов функций

```bash
from src.decorators import log

@log(filename="logs.txt")
def my_function(x: int, y: int) -> int:
    return x + y

result = my_function(3, 5)
# В файл logs.txt запишется: "2026-06-22 12:00:00 my_function ok"
```

### 9. Тестирование

Для тестирования модулей  выполните следующие шаги:

Убедитесь, что у вас установлен Python и все зависимости проекта.

Перейдите в корневую директорию проекта.

Запустите тесты для модулей:

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
```bash
python -m pytest tests/test_utils.py
```
```bash
python -m pytest tests/test_external_api.py
```

### 10. Структура проекта

- `masks.py:`-  Скрипт реализует маскрировку карт и транзакций по ним.

- `widget.py:` Скрипт для визуализации отображения номера карты.

- `proccessing.py:`-  Скрипт реализует обработку и сортировку транзакций.

- `generators.py:` -  Скрипт реализует описание и фильтрацию транзакций по картам.

- `decorators.py:` -  Скрипт декоратор регистрирующий детали выполнения функций.

- `utils.py:` -  Скрипт реализует функцию чтения файла json
  
- 'transactions.py' - Скрипт реализует функцию чтения файла Csv

- `external_api.py:` -  Скрипт реализует конвертацию EUR или USD в RUB

- `test_masks.py:` - модкль для тестрирования маскировки карт и транзакций

- `test_proccesings.py:` - модуль для тестирования транзакций по картам

- `test_widget.py:` - модуль для тестирования данных по картам

- `test_generators.py:` - модуль для тестрирования генераторов и функций

- `test_decorators.py` - модуль для тестирования декоратора функции

- `test_utils.py` - модуль для тестрирования функции чтения json файла

- `test_transactions.py` - модуль для тестрирования функции чтения csv файла

- `test_external.py` - модуль для тестирования функции конвертации USD и EUR в RUB

- `.env` - модуль безопасности чувствительных дынных

- `requirements.txt:` -  Список зависимостей.


### Лицензия

Этот проект распространяется под лицензией MIT
