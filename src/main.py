from src.bank_search import process_bank_search
from src.transactions import transactions, transactions_ecxel
from src.utils import read_json_file


def format_date(date_string: str) -> str:
    """
    Преобразует дату из ISO-формата в формат ДД.ММ.ГГГГ.

    :param date_string: Дата в формате 'YYYY-MM-DDTHH:MM:SS'.
    :return: Строка в формате 'ДД.ММ.ГГГГ'.
    """
    if len(date_string) < 10:
        return date_string
    return f"{date_string[8:10]}.{date_string[5:7]}.{date_string[0:4]}"


def mask_account(account_string: str) -> str:
    """
    Маскирует номер счёта или карты.

    Для счёта оставляет последние 4 цифры после 'Счет **'.
    Для карты маскирует среднюю часть номера.

    :param account_string: Строка с типом и номером счёта/карты.
    :return: Замаскированная строка.
    """
    if not account_string:
        return ""
    if account_string.startswith("Счет"):
        return f"Счет **{account_string[-4:]}"
    parts = account_string.split()
    if len(parts) >= 2:
        card_name = " ".join(parts[:-1])
        card_number = parts[-1]
        if len(card_number) >= 4:
            masked = f"{card_number[:2]}** **** {card_number[-4:]}"
            return f"{card_name} {masked}"
    return account_string


def format_transaction(transaction: dict) -> str:
    """
    Форматирует транзакцию для вывода в консоль.

    :param transaction: Словарь с данными о транзакции.
    :return: Строка с отформатированной информацией.
    """
    lines: list[str] = []
    date = format_date(transaction.get("date", ""))
    description = transaction.get("description", "")
    lines.append(f"{date} {description}")

    from_field = transaction.get("from")
    to_field = transaction.get("to")
    if from_field and to_field:
        masked_from = mask_account(from_field)
        masked_to = mask_account(to_field)
        lines.append(f"{masked_from} -> {masked_to}")
    elif to_field:
        lines.append(mask_account(to_field))

    amount = transaction.get("operationAmount", {}).get("amount", "")
    currency = transaction.get("operationAmount", {}).get("currency", {}).get("name", "")
    lines.append(f"Сумма: {amount} {currency}")
    return "\n".join(lines)


def load_data(choice: str) -> list[dict]:
    """
    Загружает данные из файла в зависимости от выбора пользователя.

    :param choice: Выбор пользователя ('1', '2' или '3').
    :return: Список словарей с транзакциями.
    """
    if choice == "1":
        path = input("Введите путь к JSON-файлу: ").strip()
        return read_json_file(path)
    if choice == "2":
        path = input("Введите путь к CSV-файлу: ").strip()
        return transactions(path)
    path = input("Введите путь к XLSX-файлу: ").strip()
    return transactions_ecxel(path)


def get_source_name(choice: str) -> str:
    """
    Возвращает читаемое имя источника данных.

    :param choice: Выбор пользователя ('1', '2' или '3').
    :return: Название формата файла.
    """
    return {"1": "JSON", "2": "CSV", "3": "XLSX"}.get(choice, "")


def ask_yes_no(question: str) -> bool:
    """
    Задаёт пользователю вопрос с вариантами Да/Нет.

    :param question: Текст вопроса.
    :return: True, если пользователь ответил положительно.
    """
    print(question)
    answer = input().strip().lower()
    return answer in ("да", "yes", "y")


def ask_status() -> str:
    """
    Запрашивает у пользователя статус операции с валидацией.

    :return: Валидный статус в верхнем регистре.
    """
    valid = {"executed", "canceled", "pending"}
    while True:
        print("Введите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")
        status = input().strip()
        if status.lower() in valid:
            return status.upper()
        print(f'Статус операции "{status}" недоступен.')


def main() -> None:
    """
    Основная функция программы.

    Реализует пользовательский интерфейс для работы с банковскими
    транзакциями: загрузка данных, фильтрация по статусу, сортировка,
    фильтрация по валюте и поиск по слову в описании.
    """
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

    data = load_data(choice)
    print(f"Для обработки выбран {get_source_name(choice)}-файл.")

    status = ask_status()
    filtered: list[dict] = [op for op in data if op.get("state", "").upper() == status]
    print(f'Операции отфильтрованы по статусу "{status}"')

    if ask_yes_no("Отсортировать операции по дате? Да/Нет"):
        print("Отсортировать по возрастанию или по убыванию?")
        order = input().strip().lower()
        reverse = "убыв" in order
        filtered.sort(key=lambda x: x.get("date", ""), reverse=reverse)

    if ask_yes_no("Выводить только рублевые транзакции? Да/Нет"):
        filtered = [op for op in filtered if op.get("operationAmount", {}).get("currency", {}).get("code") == "RUB"]

    if ask_yes_no("Отфильтровать список транзакций " "по определенному слову в описании? Да/Нет"):
        word = input("Введите слово для поиска: ").strip()
        filtered = process_bank_search(filtered, word)

    print("Распечатываю итоговый список транзакций...")
    print()
    if not filtered:
        print("Не найдено ни одной транзакции, подходящих под ваши " "условия фильтрации")
        return

    print(f"Всего банковских операций в выборке: {len(filtered)}")
    print()
    for transaction in filtered:
        print(format_transaction(transaction))
        print()


if __name__ == "__main__":
    main()
