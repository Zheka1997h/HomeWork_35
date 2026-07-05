# -*- coding: utf-8 -*-
"""Главный модуль банковского процессора."""

import json
import os
import subprocess
from typing import Any, Callable, Dict, List

from src.bank_search import process_bank_operations, process_bank_search
from src.decorators import log
from src.external_api import convert_transaction_to_rub, get_exchange_rate
from src.generators import card_number_generator, filter_by_currency, transaction_descriptions
from src.masks import get_mask_account, get_mask_card_number
from src.proccessing import filter_by_state, sort_by_date
from src.transactions import transactions, transactions_ecxel
from src.utils import read_json_file
from src.widget import get_date, mask_account_card

# ==================== ПУТИ К ФАЙЛАМ ====================
DEFAULT_JSON_PATH: str = r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\operations.json"
DEFAULT_CSV_PATH: str = r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\transactions.csv"
DEFAULT_EXCEL_PATH: str = r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\transactions_excel.xlsx"
DEFAULT_SAVE_PATH: str = r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\result.json"

# ==================== СОСТОЯНИЕ ПРИЛОЖЕНИЯ ====================
app_state: Dict[str, List[Dict[str, Any]]] = {
    "transactions_data": [],
    "filtered_data": [],
}

# Тип для функций-загрузчиков файлов
FileLoader = Callable[[str], List[Dict[str, Any]]]


# ==================== ОЧИСТКА КОНСОЛИ ====================
def clear_screen() -> None:
    """Очищает консоль. Работает в PyCharm Run, VS Code Run, терминалах."""
    try:
        if os.name == "nt":
            subprocess.run("cls", shell=True, check=False)
        else:
            subprocess.run("clear", shell=False, check=False)
    except Exception:
        print("\033[H\033[2J", end="", flush=True)
        print("\n" * 50)


# ==================== ОБЁРТКИ С ЛОГИРОВАНИЕМ ====================
@log()
def load_json_data(path: str) -> List[Dict[str, Any]]:
    """Загружает данные из JSON файла."""
    result: List[Dict[str, Any]] = read_json_file(path)
    return result


@log()
def load_csv_data(path: str) -> List[Dict[str, Any]]:
    """Загружает данные из CSV файла."""
    result: List[Dict[str, Any]] = transactions(path)
    return result


@log()
def load_excel_data(path: str) -> List[Dict[str, Any]]:
    """Загружает данные из Excel файла."""
    result: List[Dict[str, Any]] = transactions_ecxel(path)
    return result


@log()
def search_ops(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """Ищет операции по описанию."""
    result: List[Dict[str, Any]] = process_bank_search(data, search)
    return result


@log()
def filter_state(data: List[Dict[str, Any]], state: str) -> List[Dict[str, Any]]:
    """Фильтрует операции по статусу."""
    result: List[Dict[str, Any]] = filter_by_state(data, state)
    return result


@log()
def sort_date(data: List[Dict[str, Any]], desc: bool) -> List[Dict[str, Any]]:
    """Сортирует операции по дате."""
    result: List[Dict[str, Any]] = sort_by_date(data, desc)
    return result


@log()
def filter_currency(data: List[Dict[str, Any]], cur: str) -> List[Dict[str, Any]]:
    """Фильтрует операции по валюте."""
    result: List[Dict[str, Any]] = list(filter_by_currency(data, cur))
    return result


@log()
def mask_card(num: str) -> str:
    """Маскирует номер карты."""
    result: str = get_mask_card_number(num)
    return result


@log()
def mask_acc(num: str) -> str:
    """Маскирует номер счёта."""
    result: str = get_mask_account(num)
    return result


@log()
def mask_card_type(info: str) -> str:
    """Маскирует карту по типу."""
    result: str = mask_account_card(info)
    return result


@log()
def get_rate(cur: str) -> float:
    """Получает курс валюты."""
    result: float = get_exchange_rate(cur)
    return result


@log()
def count_categories(data: List[Dict[str, Any]], cats: List[str]) -> Dict[str, int]:
    """Подсчитывает операции по категориям."""
    result: Dict[str, int] = process_bank_operations(data, cats)
    return result


@log()
def save_json_data(data: List[Dict[str, Any]], path: str) -> int:
    """Сохраняет данные в JSON. Возвращает количество записей."""
    folder: str = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(data)


# ==================== УТИЛИТЫ ====================
def header(title: str) -> None:
    """Печатает заголовок."""
    print(f"\n── {title} {'─' * (50 - len(title))}")


def info(msg: str) -> None:
    """Печатает информационное сообщение."""
    print(f"  {msg}")


def err(msg: str) -> None:
    """Печатает сообщение об ошибке."""
    print(f"  ❌ {msg}")


def ok(msg: str) -> None:
    """Печатает сообщение об успехе."""
    print(f"  ✅ {msg}")


def pause() -> None:
    """Ожидает нажатия Enter."""
    input("\n  ⏎ Enter — продолжить...")


def load_file(file_type: str, path: str, loader: FileLoader) -> None:
    """Загружает файл через переданную функцию-загрузчик."""
    header(f"Загрузка {file_type}")
    info(f"📁 {path}")

    if not os.path.isfile(path):
        err(f"Файл не найден: {path}")
        return

    try:
        data: List[Dict[str, Any]] = loader(path)
        app_state["transactions_data"] = data
        app_state["filtered_data"] = data.copy()
        ok(f"Загружено: {len(data)} транзакций")
    except Exception as e:
        err(f"Ошибка: {e}")


def print_transactions(data: List[Dict[str, Any]], limit: int = 10) -> None:
    """Печатает список транзакций."""
    for i, t in enumerate(data[:limit], 1):
        date: str = t.get("date", "")[:10]
        desc: str = t.get("description", "")[:35]
        state: str = t.get("state", "?")
        operation_amount: Dict[str, Any] = t.get("operationAmount", {})
        amount: str = operation_amount.get("amount", "0")
        currency_info: Dict[str, Any] = operation_amount.get("currency", {})
        cur: str = currency_info.get("code", "?")
        print(f"  {i:2}. [{state[:3]}] {date} | {amount:>10} {cur} | {desc}")

    if len(data) > limit:
        print(f"  ... и ещё {len(data) - limit} записей")


# ==================== ДЕЙСТВИЯ ====================
def action_load_json() -> None:
    """Загружает JSON файл."""
    load_file("JSON", DEFAULT_JSON_PATH, load_json_data)


def action_load_csv() -> None:
    """Загружает CSV файл."""
    load_file("CSV", DEFAULT_CSV_PATH, load_csv_data)


def action_load_excel() -> None:
    """Загружает Excel файл."""
    load_file("Excel", DEFAULT_EXCEL_PATH, load_excel_data)


def action_show_all() -> None:
    """Показывает все транзакции."""
    header("Все транзакции")
    data: List[Dict[str, Any]] = app_state["filtered_data"]
    if not data:
        err("Данные не загружены")
        return
    info(f"Всего: {len(data)}")
    print_transactions(data, limit=20)


def action_search() -> None:
    """Ищет транзакции по описанию."""
    header("Поиск по описанию")
    if not app_state["transactions_data"]:
        err("Сначала загрузите данные")
        return

    text: str = input("  🔎 Запрос: ").strip()
    if not text:
        err("Пустой запрос")
        return

    results: List[Dict[str, Any]] = search_ops(app_state["transactions_data"], text)
    app_state["filtered_data"] = results
    header(f"Результаты поиска: '{text}'")
    ok(f"Найдено: {len(results)}")
    print_transactions(results)


def action_filter_state() -> None:
    """Фильтрует транзакции по статусу."""
    header("Фильтр по статусу")
    if not app_state["transactions_data"]:
        err("Сначала загрузите данные")
        return

    print("  1) EXECUTED  2) CANCELED  3) PENDING")
    choice: str = input("  👉 Выбор: ").strip()
    state_map: Dict[str, str] = {"1": "EXECUTED", "2": "CANCELED", "3": "PENDING"}

    if choice not in state_map:
        err("Неверный выбор")
        return

    state: str = state_map[choice]
    results: List[Dict[str, Any]] = filter_state(app_state["transactions_data"], state)
    app_state["filtered_data"] = results
    header(f"Фильтр: {state}")
    ok(f"Найдено: {len(results)} транзакций")
    print_transactions(results)


def action_sort_date() -> None:
    """Сортирует транзакции по дате."""
    header("Сортировка по дате")
    if not app_state["filtered_data"]:
        err("Нет данных")
        return

    print("  1) По убыванию (новые)  2) По возрастанию (старые)")
    choice: str = input("  👉 Выбор: ").strip()

    if choice == "1":
        desc: bool = True
        label: str = "убыванию"
    elif choice == "2":
        desc = False
        label = "возрастанию"
    else:
        err("Неверный выбор")
        return

    results: List[Dict[str, Any]] = sort_date(app_state["filtered_data"], desc)
    app_state["filtered_data"] = results
    header(f"Сортировка по {label}")
    ok("Готово")
    print_transactions(results)


def action_filter_currency() -> None:
    """Фильтрует транзакции по валюте."""
    header("Фильтр по валюте")
    if not app_state["transactions_data"]:
        err("Сначала загрузите данные")
        return

    cur: str = input("  💱 Валюта (USD/EUR/RUB): ").strip().upper()
    if not cur:
        err("Валюта не указана")
        return

    results: List[Dict[str, Any]] = filter_currency(app_state["transactions_data"], cur)
    app_state["filtered_data"] = results
    header(f"Фильтр по валюте: {cur}")
    ok(f"Найдено: {len(results)} транзакций")
    print_transactions(results)


def action_mask_card() -> None:
    """Маскирует номер карты."""
    header("Маскировка карты (16 цифр)")
    num: str = input("  💳 Номер: ").strip()
    if not num:
        err("Пустой ввод")
        return
    try:
        result: str = mask_card(num)
        header("Результат маскировки карты")
        ok(f"{num}  →  {result}")
    except ValueError as e:
        header("Ошибка")
        err(str(e))


def action_mask_account() -> None:
    """Маскирует номер счёта."""
    header("Маскировка счёта (20 цифр)")
    num: str = input("  🔐 Номер: ").strip()
    if not num:
        err("Пустой ввод")
        return
    try:
        result: str = mask_acc(num)
        header("Результат маскировки счёта")
        ok(f"{num}  →  {result}")
    except ValueError as e:
        header("Ошибка")
        err(str(e))


def action_mask_card_type() -> None:
    """Маскирует карту по типу."""
    header("Маскировка по типу")
    info("Пример: Visa 1234567890123456 / Счет 12345678901234567890")
    card_info: str = input("  🎴 Ввод: ").strip()
    if not card_info:
        err("Пустой ввод")
        return
    try:
        result: str = mask_card_type(card_info)
        header("Результат маскировки")
        ok(f"{card_info}  →  {result}")
    except ValueError as e:
        header("Ошибка")
        err(str(e))


def action_convert_date() -> None:
    """Преобразует дату из ISO в ДД.ММ.ГГГГ."""
    header("Преобразование даты")
    info("Формат: 2024-01-15T12:30:00")
    date_str: str = input("  📅 Ввод: ").strip()
    if not date_str:
        err("Пустой ввод")
        return
    try:
        result: str = get_date(date_str[:10])
        header("Преобразование даты")
        ok(f"{date_str}  →  {result}")
    except ValueError:
        header("Ошибка")
        err("Неверный формат даты")


def action_get_rate() -> None:
    """Получает курс валюты."""
    header("Курс валюты")
    cur: str = input("  💹 Валюта (USD/EUR/GBP): ").strip().upper()
    if not cur:
        err("Валюта не указана")
        return
    try:
        info("⏳ Запрос к API...")
        rate: float = get_rate(cur)
        header(f"Курс {cur} к RUB")
        ok(f"1 {cur} = {rate:.4f} RUB")
    except Exception as e:
        header("Ошибка")
        err(str(e))


def action_convert_to_rub() -> None:
    """Конвертирует транзакции в рубли."""
    header("Конвертация в рубли")
    data: List[Dict[str, Any]] = app_state["filtered_data"]
    if not data:
        err("Нет данных")
        return

    total: float = 0.0
    count: int = 0
    for i, t in enumerate(data[:10], 1):
        try:
            rub: float = convert_transaction_to_rub(t)
            total += rub
            count += 1
            desc: str = t.get("description", "")[:30]
            print(f"  {i:2}. {rub:>10.2f} RUB | {desc}")
        except Exception as e:
            print(f"  {i:2}. Ошибка: {e}")

    if len(data) > 10:
        print(f"  ... и ещё {len(data) - 10} транзакций")
    info(f"Итого: {total:.2f} RUB ({count} конверт.)")


def action_count_categories() -> None:
    """Подсчитывает операции по категориям."""
    header("Подсчёт по категориям")
    data: List[Dict[str, Any]] = app_state["filtered_data"]
    if not data:
        err("Нет данных")
        return

    info("Пример: Перевод организации,Оплата услуг")
    cats_str: str = input("  📊 Категории: ").strip()
    if not cats_str:
        err("Пустой ввод")
        return

    cats: List[str] = [c.strip() for c in cats_str.split(",")]
    results: Dict[str, int] = count_categories(data, cats)
    header("Результаты подсчёта")
    for cat, count in results.items():
        print(f"  • {cat}: {count}")


def action_statistics() -> None:
    """Показывает статистику по транзакциям."""
    header("Статистика")
    data: List[Dict[str, Any]] = app_state["filtered_data"]
    if not data:
        err("Нет данных")
        return

    info(f"Всего транзакций: {len(data)}")

    currencies: Dict[str, int] = {}
    states: Dict[str, int] = {}
    for t in data:
        operation_amount: Dict[str, Any] = t.get("operationAmount", {})
        currency_info: Dict[str, Any] = operation_amount.get("currency", {})
        cur: str = currency_info.get("code", "?")
        currencies[cur] = currencies.get(cur, 0) + 1
        st: str = t.get("state", "?")
        states[st] = states.get(st, 0) + 1

    print("\n  💱 Валюты:")
    for cur, count in currencies.items():
        print(f"     • {cur}: {count}")
    print("  🎯 Статусы:")
    for st, count in states.items():
        print(f"     • {st}: {count}")


def action_descriptions() -> None:
    """Показывает описания транзакций."""
    header("Описания транзакций")
    data: List[Dict[str, Any]] = app_state["filtered_data"]
    if not data:
        err("Нет данных")
        return

    descriptions: List[str] = list(transaction_descriptions(data))
    for i, desc in enumerate(descriptions[:20], 1):
        print(f"  {i:2}. {desc}")
    if len(descriptions) > 20:
        print(f"  ... и ещё {len(descriptions) - 20}")


def action_generate_cards() -> None:
    """Генерирует номера карт."""
    header("Генератор номеров карт")
    try:
        start: int = int(input("  От: ").strip())
        stop: int = int(input("  До: ").strip())
        if stop <= start:
            err("«До» должно быть больше «От»")
            return
        if stop - start > 100:
            err("Максимум 100 номеров")
            return

        header(f"Номера карт ({start} — {stop})")
        for i, card in enumerate(card_number_generator(start, stop), 1):
            print(f"  {i:2}. {card}")
    except ValueError:
        err("Введите числа")


def action_save() -> None:
    """Автоматически сохраняет в DEFAULT_SAVE_PATH."""
    header("Сохранение результата")
    data: List[Dict[str, Any]] = app_state["filtered_data"]

    if not data:
        err("Нет данных для сохранения")
        return

    info(f"📁 Сохраняем в: {DEFAULT_SAVE_PATH}")

    try:
        count: int = save_json_data(data, DEFAULT_SAVE_PATH)
        ok(f"Сохранено: {count} записей")
        info(f"📄 Файл: {os.path.abspath(DEFAULT_SAVE_PATH)}")
    except Exception as e:
        err(f"Ошибка сохранения: {e}")


def action_clear() -> None:
    """Очищает данные."""
    app_state["transactions_data"] = []
    app_state["filtered_data"] = []
    header("Очистка данных")
    ok("Данные очищены")


# ==================== МЕНЮ ====================
# Тип элемента меню: (номер, название, функция или None)
MenuItem = tuple[str, str, Callable[[], None] | None]

MENU: List[MenuItem] = [
    ("1", "Загрузить JSON", action_load_json),
    ("2", "Загрузить CSV", action_load_csv),
    ("3", "Загрузить Excel", action_load_excel),
    ("4", "Показать данные", action_show_all),
    ("5", "Поиск", action_search),
    ("6", "Фильтр по статусу", action_filter_state),
    ("7", "Сортировка по дате", action_sort_date),
    ("8", "Фильтр по валюте", action_filter_currency),
    ("9", "Маска карты", action_mask_card),
    ("10", "Маска счёта", action_mask_account),
    ("11", "Маска по типу", action_mask_card_type),
    ("12", "Дата ISO → ДД.ММ.ГГГГ", action_convert_date),
    ("13", "Курс валюты", action_get_rate),
    ("14", "Конвертация в RUB", action_convert_to_rub),
    ("15", "По категориям", action_count_categories),
    ("16", "Статистика", action_statistics),
    ("17", "Описания", action_descriptions),
    ("18", "Генератор карт", action_generate_cards),
    ("19", "Сохранить результат", action_save),
    ("20", "Очистить данные", action_clear),
    ("0", "Выход", None),
]


def print_menu() -> None:
    """Меню всегда печатается СВЕРХУ экрана."""
    clear_screen()

    data: List[Dict[str, Any]] = app_state["transactions_data"]
    filtered: List[Dict[str, Any]] = app_state["filtered_data"]

    status: str = f"Загружено: {len(data)} | Отфильтровано: {len(filtered)}" if data else "Данные не загружены"

    print(f"{'═' * 72}")
    print("  🏦 БАНКОВСКИЙ ПРОЦЕССОР v6.0")
    print(f"  {status}")
    print(f"{'═' * 72}")

    rows: List[List[MenuItem]] = [list(MENU[i : i + 3]) for i in range(0, len(MENU), 3)]

    for row in rows:
        cells: List[str] = []
        for num, name, _ in row:
            cells.append(f"[{num:>2}] {name:<22}")
        print("  " + "  ".join(cells))

    print(f"{'═' * 72}")


def main() -> None:
    """Главная функция приложения."""
    clear_screen()
    print("🏦 Запуск банковского процессора...")
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    actions: Dict[str, Callable[[], None]] = {num: action for num, _, action in MENU if action is not None}

    while True:
        print_menu()
        choice: str = input("\n  👉 Ваш выбор: ").strip()

        if choice == "0":
            clear_screen()
            print("\n  👋 До свидания!\n")
            break

        action: Callable[[], None] | None = actions.get(choice)
        if action is not None:
            action()
        else:
            err("Неверный выбор")

        pause()


if __name__ == "__main__":
    main()
