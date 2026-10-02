"""Модуль с классом DBManager для работы с данными в БД."""

import psycopg2
from psycopg2.extensions import connection

import config


class DBManager:
    """Класс для работы с данными в БД PostgreSQL.

    Предоставляет методы для получения информации о компаниях
    и вакансиях, хранящихся в базе данных.
    """

    def __init__(self) -> None:
        """Инициализирует подключение к БД."""
        self.conn: connection = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )

    def close(self) -> None:
        """Закрывает подключение к БД."""
        if self.conn:
            self.conn.close()

    def get_companies_and_vacancies_count(self) -> list[tuple[str, int]]:
        """Получает список всех компаний и количество вакансий у каждой.

        Returns:
            Список кортежей (название_компании, количество_вакансий).
        """
        query = """
            SELECT e.company_name, COUNT(v.vacancy_id) AS vacancy_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.company_name
            ORDER BY vacancy_count DESC;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_all_vacancies(self) -> list[tuple[str, str, int | None, str]]:
        """Получает список всех вакансий.

        Returns:
            Список кортежей (компания, вакансия, зарплата, ссылка).
        """
        query = """
            SELECT e.company_name, v.vacancy_name, v.salary, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY e.company_name, v.vacancy_name;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_avg_salary(self) -> float | None:
        """Получает среднюю зарплату по всем вакансиям.

        Returns:
            Средняя зарплата или None, если данных о зарплатах нет.
        """
        query = """
            SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            return result[0] if result and result[0] is not None else None

    def get_vacancies_with_higher_salary(self) -> list[tuple[str, str, int, str]]:
        """Получает вакансии с зарплатой выше средней.

        Returns:
            Список кортежей (компания, вакансия, зарплата, ссылка).
        """
        query = """
            SELECT e.company_name, v.vacancy_name, v.salary, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.salary > (
                SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL
            )
            ORDER BY v.salary DESC;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple[str, str, int | None, str]]:
        """Получает вакансии, в названии которых есть ключевое слово.

        Args:
            keyword: Ключевое слово для поиска.

        Returns:
            Список кортежей (компания, вакансия, зарплата, ссылка).
        """
        query = """
            SELECT e.company_name, v.vacancy_name, v.salary, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.vacancy_name ILIKE %s
            ORDER BY e.company_name;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (f"%{keyword}%",))
            return cur.fetchall()