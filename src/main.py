"""Точка входа в приложение.

Запускает весь процесс: создание БД, таблиц,
загрузку данных и взаимодействие с пользователем.
"""

import psycopg2
import config
from src.api_hh import HHApi
from src.database import create_database, create_tables, get_connection
from src.user_interaction import user_interaction


def load_employers_data() -> None:
    """Загружает данные о работодателях в таблицу employers."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for company in config.COMPANIES:
                cur.execute(
                    """
                    INSERT INTO employers (employer_id, company_name, url)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (employer_id) DO NOTHING;
                    """,
                    (company["id"], company["name"],
                     f"https://hh.ru/employer/{company['id']}"),
                )
        conn.commit()
        print("Данные о работодателях загружены.")
    finally:
        conn.close()


def load_vacancies_data() -> None:
    """Загружает данные о вакансиях в таблицу vacancies."""
    conn = get_connection()
    api = HHApi()
    try:
        with conn.cursor() as cur:
            for company in config.COMPANIES:
                print(f"Загрузка вакансий компании '{company['name']}'...")
                try:
                    vacancies = api.get_employer_vacancies(company["id"])
                except Exception as e:
                    print(f"  Ошибка при загрузке: {e}")
                    continue

                for vac in vacancies:
                    salary = api.parse_salary(vac.get("salary"))
                    cur.execute(
                        """
                        INSERT INTO vacancies
                            (vacancy_id, employer_id, vacancy_name, salary, url)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (vacancy_id) DO NOTHING;
                        """,
                        (
                            int(vac["id"]),
                            company["id"],
                            vac["name"],
                            salary,
                            vac.get("alternate_url"),
                        ),
                    )
                conn.commit()
                print(f"  Загружено вакансий: {len(vacancies)}")
        print("Все вакансии успешно загружены.")
    finally:
        conn.close()


def main() -> None:
    """Главная функция приложения."""
    print("Создание базы данных...")
    create_database()

    print("Создание таблиц...")
    create_tables()

    print("Загрузка данных о работодателях...")
    load_employers_data()

    print("Загрузка данных о вакансиях (может занять время)...")
    load_vacancies_data()

    print("\nЗапуск интерфейса пользователя...")
    user_interaction()


if __name__ == "__main__":
    main()