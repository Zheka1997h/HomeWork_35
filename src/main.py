import json
import logging
from pathlib import Path

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import (get_top_cashback_categories, investment_bank, search_by_phone,
                          search_transfers_to_individuals, simple_search)
from src.utils import df_to_list_of_dicts, read_excel_data
from src.views import get_events_page_data, get_main_page_data

logging.basicConfig(level=logging.INFO)


def main():
    project_root = Path(__file__).parent.parent

    settings_path = project_root / "user_settings.json"
    data_path = project_root / "data" / "operations.xlsx"

    # 2. Загружаем настройки и данные
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except FileNotFoundError:
        logging.error(f"Файл настроек не найден! Проверь путь: {settings_path}")
        return

    # Передаем путь как строку в нашу функцию
    df = read_excel_data(str(data_path))
    if df.empty:
        logging.error("Нет данных для работы или файл Excel пуст!")
        return

    # 3. Тестируем Главную страницу
    print("--- ГЛАВНАЯ СТРАНИЦА ---")
    main_page = get_main_page_data("2021-12-20 14:30:00", df, settings)
    print(json.dumps(main_page, ensure_ascii=False, indent=4))

    # 4. Тестируем Страницу Событий
    print("\n--- СТРАНИЦА СОБЫТИЯ (Месяц) ---")
    events_page = get_events_page_data("2021-12-20 14:30:00", df, settings, period="M")
    print(json.dumps(events_page, ensure_ascii=False, indent=4))

    # 5. Тестируем Сервисы
    print("\n--- СЕРВИСЫ ---")
    data_list = df_to_list_of_dicts(df)

    top_cashback = get_top_cashback_categories(data_list, 2021, 12)
    print("Топ кешбэк категорий:", top_cashback)

    search_res = simple_search("Пятёрочка", data_list)
    print(f"Найдено транзакций по запросу 'Пятёрочка': {len(search_res)}")

    phone_res = search_by_phone(data_list)
    print(f"Найдено транзакций с телефонами: {len(phone_res)}")

    transfer_res = search_transfers_to_individuals(data_list)
    print(f"Найдено переводов физлицам: {len(transfer_res)}")

    invest_res = investment_bank("2021-12", data_list, 50)
    print(f"Сумма для инвесткопилки (шаг 50): {invest_res}")

    # 6. Тестируем Отчеты
    print("\n--- ОТЧЕТЫ ---")
    spending_by_category(df, "Супермаркеты", date="2021-12-20")
    spending_by_weekday(df, date="2021-12-20")
    spending_by_workday(df, date="2021-12-20")
    print("Отчеты сгенерированы и сохранены в CSV.")


if __name__ == "__main__":
    main()
