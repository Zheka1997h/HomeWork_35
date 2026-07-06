# -*- coding: utf-8 -*-
"""Главный модуль программы.

Реализует пользовательский интерфейс для работы с банковскими транзакциями:
загрузка данных из JSON/CSV/XLSX (пути захардкожены), фильтрация, сортировка,
поиск, конвертация валют и вывод.

Использует функции из модулей:
- src.utils: read_json_file
- src.transactions: transactions, transactions_ecxel
- src.processing: filter_by_state, sort_by_date
- src.generators: filter_by_currency, transaction_descriptions,
                  card_number_generator, check_card_number
- src.widget: mask_account_card, get_date
- src.masks: get_mask_card_number, get_mask_account
- src.bank_search: process_bank_search
- src.external_api: convert_transaction_to_rub, get_exchange_rate
- src.decorators: log
"""

from typing import List, Optional, Dict, Any, cast

from src.bank_search import process_bank_search
from src.decorators import log
from src.external_api import convert_transaction_to_rub, get_exchange_rate
from src.generators import card_number_generator, check_card_number, filter_by_currency, transaction_descriptions
from src.masks import get_mask_account, get_mask_card_number
from src.proccessing import filter_by_state, sort_by_date
from src.transactions import transactions, transactions_ecxel
from src.utils import read_json_file
from src.widget import get_date, mask_account_card

# ==================== 🆕 ПУТИ К ФАЙЛАМ ====================

# Захардкоженные пути к файлам с данными
JSON_FILE_PATH = r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\operations.json"
CSV_FILE_PATH = r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\transactions.csv"
XLSX_FILE_PATH = r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\transactions_excel.xlsx"

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================


@log()
def is_valid_card_number(card_number: str) -> bool:
    """Проверяет, является ли строка валидным номером карты.

    Использует check_card_number из модуля generators.

    Args:
        card_number: Строка с номером карты.

    Returns:
        True, если номер валиден, иначе False.
    """
    try:
        check_card_number(card_number)
        return len(card_number) == 16 and card_number.isdigit()
    except ValueError:
        return False


@log()
def mask_from_to_field(field_value: str) -> str:
    """Маскирует поле 'from' или 'to' транзакции.

    Использует функции из модулей widget и masks:
    - mask_account_card (widget) — для карт
    - get_mask_account (masks) — для счетов
    - get_mask_card_number (masks) — для номеров карт

    Args:
        field_value: Строка вида 'Visa Platinum 7492650272063783'
                     или 'Счет 1234...'.

    Returns:
        Замаскированная строка.
    """
    if not field_value:
        return ""

    # Для счёта — используем get_mask_account из masks
    if field_value.startswith("Счет"):
        digits = "".join(filter(str.isdigit, field_value))
        if len(digits) >= 4:
            return f"Счет {get_mask_account(digits)}"
        return field_value

    # Для карты — используем mask_account_card из widget
    parts = field_value.split()
    if len(parts) < 2:
        return field_value

    card_type = parts[0]  # noqa
    card_number = "".join(filter(str.isdigit, parts[-1]))

    # Валидация через check_card_number из generators
    if not is_valid_card_number(card_number):
        return field_value

    # Маскирование через get_mask_card_number из masks
    if len(card_number) == 16:
        masked_number = get_mask_card_number(card_number)
        card_name = " ".join(parts[:-1])
        return f"{card_name} {masked_number}"

    # Альтернативное маскирование через mask_account_card из widget
    try:
        result: str = mask_account_card(field_value)
        return result
    except ValueError:
        return field_value


@log()
def format_date_iso(date_string: str) -> str:
    """Форматирует дату из ISO в ДД.ММ.ГГГГ.

    Использует get_date из модуля widget для дат стандартной длины.
    Для дат с миллисекундами обрезает до 10 символов.

    Args:
        date_string: Дата в формате 'YYYY-MM-DDTHH:MM:SS...'.

    Returns:
        Строка в формате 'ДД.ММ.ГГГГ'.
    """
    if not date_string or len(date_string) < 10:
        return date_string

    # Обрезаем до 10 символов (YYYY-MM-DD) для get_date
    date_part = date_string[:10]

    try:
        # Используем get_date из widget
        result: str = get_date(date_part)
        return result
    except ValueError:
        # Fallback: ручное форматирование
        return f"{date_part[8:10]}.{date_part[5:7]}.{date_part[0:4]}"


@log()
def get_amount_in_rub(transaction: dict) -> Optional[float]:
    """Получает сумму транзакции в рублях.

    Использует convert_transaction_to_rub из external_api.

    Args:
        transaction: Словарь с данными о транзакции.

    Returns:
        Сумма в рублях (float) или None при ошибке конвертации.
    """
    try:
        result: float = convert_transaction_to_rub(transaction)
        return result
    except Exception:
        return None


@log()
def format_transaction(transaction: dict, convert_to_rub: bool = False) -> str:
    """Форматирует транзакцию для вывода в консоль.

    Использует:
    - format_date_iso (с get_date из widget)
    - mask_from_to_field (с mask_account_card, get_mask_card_number,
                          get_mask_account из masks/widget)
    - get_amount_in_rub (с convert_transaction_to_rub из external_api)

    Args:
        transaction: Словарь с данными о транзакции.
        convert_to_rub: Если True — добавляет сумму в рублях.

    Returns:
        Отформатированная строка.
    """
    lines: List[str] = []

    # Дата и описание
    date = format_date_iso(transaction.get("date", ""))
    description = transaction.get("description", "")
    lines.append(f"{date} {description}")

    # От / Кому (с маскированием)
    from_field = transaction.get("from")
    to_field = transaction.get("to")
    if from_field and to_field:
        lines.append(f"{mask_from_to_field(from_field)} -> {mask_from_to_field(to_field)}")
    elif to_field:
        lines.append(mask_from_to_field(to_field))

    # Сумма и валюта
    operation_amount = transaction.get("operationAmount", {})
    amount = operation_amount.get("amount", "")
    currency_name = operation_amount.get("currency", {}).get("name", "")
    currency_code = operation_amount.get("currency", {}).get("code", "")

    # Если нужна конвертация и валюта не рубли — показываем эквивалент
    if convert_to_rub and currency_code != "RUB":
        rub_amount = get_amount_in_rub(transaction)
        if rub_amount is not None:
            lines.append(f"Сумма: {amount} {currency_name} (≈ {rub_amount:.2f} руб.)")
        else:
            lines.append(f"Сумма: {amount} {currency_name}")
    else:
        lines.append(f"Сумма: {amount} {currency_name}")

    return "\n".join(lines)


@log()
def get_all_descriptions(transactions_list: List[dict]) -> List[str]:
    """Получает все описания транзакций через генератор.

    Использует transaction_descriptions из модуля generators.

    Args:
        transactions_list: Список транзакций.

    Returns:
        Список описаний.
    """
    return list(transaction_descriptions(transactions_list))


@log()
def validate_card_numbers_in_data(transactions_list: List[dict]) -> int:
    """Считает количество валидных номеров карт в данных.

    Использует card_number_generator из generators для
    демонстрации генерации и check_card_number для валидации.

    Args:
        transactions_list: Список транзакций.

    Returns:
        Количество валидных номеров карт.
    """
    valid_count = 0

    # Демонстрация работы card_number_generator
    sample_cards = list(card_number_generator(1000000000000000, 1000000000000003))
    for card in sample_cards:
        digits = "".join(filter(str.isdigit, card))
        if is_valid_card_number(digits):
            valid_count += 1

    # Проверяем реальные данные
    for transaction in transactions_list:
        for field in ("from", "to"):
            value = transaction.get(field, "")
            if value:
                digits = "".join(filter(str.isdigit, value))
                if len(digits) == 16 and is_valid_card_number(digits):
                    valid_count += 1

    return valid_count


@log()
def calculate_total_in_rub(transactions_list: List[dict]) -> float:
    """Вычисляет общую сумму всех транзакций в рублях.

    Использует convert_transaction_to_rub из external_api
    для конвертации каждой транзакции.

    Args:
        transactions_list: Список транзакций.

    Returns:
        Общая сумма в рублях.
    """
    total = 0.0
    for transaction in transactions_list:
        rub_amount = get_amount_in_rub(transaction)
        if rub_amount is not None:
            total += rub_amount
    return round(total, 2)


@log()
def show_exchange_rates() -> None:
    """Показывает текущие курсы валют к рублю.

    Использует get_exchange_rate из external_api
    для получения курсов USD и EUR.
    """
    print("💱 Текущие курсы валют:")
    try:
        usd_rate = get_exchange_rate("USD")
        print(f"  • 1 USD = {usd_rate:.2f} RUB")
    except Exception as e:
        print(f"  • USD: не удалось получить курс ({e})")

    try:
        eur_rate = get_exchange_rate("EUR")
        print(f"  • 1 EUR = {eur_rate:.2f} RUB")
    except Exception as e:
        print(f"  • EUR: не удалось получить курс ({e})")
    print()


# ==================== ФУНКЦИИ ИНТЕРАКТИВА ====================


@log()
def ask_yes_no(question: str) -> bool:
    """Задаёт вопрос с вариантами Да/Нет.

    Args:
        question: Текст вопроса.

    Returns:
        True, если пользователь ответил положительно.
    """
    print(question)
    answer = input().strip().lower()
    return answer in ("да", "yes", "y")


@log()
def ask_status() -> str:
    """Запрашивает у пользователя статус операции с валидацией.

    Повторяет запрос при невалидном вводе, не падает в ошибку.

    Returns:
        Валидный статус в верхнем регистре.
    """
    valid = {"executed", "canceled", "pending"}
    while True:
        print("Введите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")
        status = input().strip()
        if status.lower() in valid:
            return status.upper()
        print(f'Статус операции "{status}" недоступен.')


# ==================== 🆕 ЗАГРУЗКА ДАННЫХ БЕЗ ВВОДА ПУТИ ====================


@log()
def load_data(choice: str) -> List[dict]:
    """Загружает данные из захардкоженного файла.

    🆕 Путь к файлу определяется автоматически по выбору пользователя.
    Не требует ввода пути вручную.

    Args:
        choice: Выбор пользователя ('1', '2' или '3').

    Returns:
        Список словарей с транзакциями.
    """
    if choice == "1":
        print(f"📂 Загрузка данных из JSON: {JSON_FILE_PATH}")
        result: List[Dict[str, Any]] = read_json_file(JSON_FILE_PATH)
        return result
    if choice == "2":
        print(f"📂 Загрузка данных из CSV: {CSV_FILE_PATH}")
        return cast(list[dict[str, Any]], transactions(CSV_FILE_PATH))
    print(f"📂 Загрузка данных из XLSX: {XLSX_FILE_PATH}")
    return cast(list[dict[str, Any]], transactions_ecxel(XLSX_FILE_PATH))


@log()
def get_source_name(choice: str) -> str:
    """Возвращает читаемое имя источника данных.

    Args:
        choice: Выбор пользователя ('1', '2' или '3').

    Returns:
        Название формата файла.
    """
    return {"1": "JSON", "2": "CSV", "3": "XLSX"}.get(choice, "")


# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================


@log()
def main() -> None:
    """Основная функция программы.

    Реализует пользовательский интерфейс для работы с банковскими
    транзакциями согласно ТЗ:

    1. Приветствие и выбор источника данных (JSON/CSV/XLSX).
    2. 🆕 Автоматическая загрузка данных из захардкоженного пути.
    3. Фильтрация по статусу (с повторным запросом при ошибке).
    4. Сортировка по дате (по возрастанию/убыванию).
    5. Фильтрация только рублёвых транзакций.
    6. Поиск по слову в описании.
    7. Конвертация валют в рубли (опционально).
    8. Вывод итогового списка или сообщения об отсутствии.

    Использует функции из всех модулей проекта:
    - src.utils: read_json_file
    - src.transactions: transactions, transactions_ecxel
    - src.processing: filter_by_state, sort_by_date
    - src.generators: filter_by_currency, transaction_descriptions,
                      card_number_generator, check_card_number
    - src.widget: mask_account_card, get_date
    - src.masks: get_mask_card_number, get_mask_account
    - src.bank_search: process_bank_search
    - src.external_api: convert_transaction_to_rub, get_exchange_rate
    - src.decorators: log
    """
    # ========== 1. Приветствие и выбор источника ==========
    print("Привет! Добро пожаловать в программу работы " "с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    while True:
        choice = input().strip()
        if choice in ("1", "2", "3"):
            break
        print("Неверный ввод. Введите 1, 2 или 3.")

    # ========== 2. 🆕 Автоматическая загрузка данных ==========
    data = load_data(choice)
    print(f"Для обработки выбран {get_source_name(choice)}-файл.")

    # Проверка на пустые данные
    if not data:
        print("⚠️ Файл пуст или не содержит данных.")
        return

    # ========== 3. Фильтрация по статусу ==========
    status = ask_status()
    filtered: List[dict] = filter_by_state(data, status)
    print(f'Операции отфильтрованы по статусу "{status}"')

    # ========== 4. Сортировка по дате ==========
    if ask_yes_no("Отсортировать операции по дате? Да/Нет"):
        print("Отсортировать по возрастанию или по убыванию?")
        order = input().strip().lower()
        reverse = "убыв" in order
        filtered = sort_by_date(filtered, descending=reverse)

    # ========== 5. Фильтрация по валюте (RUB) ==========
    if ask_yes_no("Выводить только рублевые транзакции? Да/Нет"):
        filtered = list(filter_by_currency(filtered, "RUB"))

    # ========== 6. Поиск по слову в описании ==========
    if ask_yes_no("Отфильтровать список транзакций " "по определенному слову в описании? Да/Нет"):
        word = input("Введите слово для поиска: ").strip()
        filtered = process_bank_search(filtered, word)

    # ========== 7. Конвертация валют в рубли ==========
    convert_to_rub = ask_yes_no("Конвертировать все суммы в рубли? Да/Нет")
    if convert_to_rub:
        # Показываем текущие курсы валют через get_exchange_rate
        show_exchange_rates()

    # ========== 8. Вывод результата ==========
    print("Распечатываю итоговый список транзакций...")
    print()

    if not filtered:
        print("Не найдено ни одной транзакции, подходящих под ваши " "условия фильтрации")
        return

    # Получаем все описания через генератор (используем transaction_descriptions)
    descriptions = get_all_descriptions(filtered)
    print(f"Всего банковских операций в выборке: {len(filtered)}")
    print(f"Уникальных описаний: {len(set(descriptions))}")

    # Проверяем валидность номеров карт (используем card_number_generator)
    valid_cards = validate_card_numbers_in_data(filtered)
    if valid_cards > 0:
        print(f"Найдено валидных номеров карт: {valid_cards}")

    # Если конвертация включена — показываем общую сумму в рублях
    if convert_to_rub:
        total_rub = calculate_total_in_rub(filtered)
        print(f"💰 Общая сумма в рублях: {total_rub:.2f} руб.")

    print()

    # Выводим каждую транзакцию с форматированием
    for transaction in filtered:
        print(format_transaction(transaction, convert_to_rub=convert_to_rub))
        print()


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    main()
