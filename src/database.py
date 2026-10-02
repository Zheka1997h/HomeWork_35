"""Модуль для создания базы данных и таблиц."""

from typing import Any

import psycopg2
from psycopg2.extensions import connection

import config


def get_connection(db_name: str | None = None) -> connection:
    """Создаёт подключение к БД PostgreSQL.

    Args:
        db_name: Имя базы данных. Если None, используется
                 имя из конфигурации.

    Returns:
        Объект подключения psycopg2.
    """
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=db_name or config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )


def create_database() -> None:
    """Создаёт базу данных для хранения вакансий.

    Если база данных уже существует, она будет удалена
    и создана заново.
    """
    conn = get_connection(config.DEFAULT_DB_NAME)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"DROP DATABASE IF EXISTS {config.DB_NAME}"
            )
            cur.execute(
                f"CREATE DATABASE {config.DB_NAME}"
            )
        print(f"База данных '{config.DB_NAME}' успешно создана.")
    finally:
        conn.close()


def create_tables() -> None:
    """Создаёт таблицы employers и vacancies в БД."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id INTEGER PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    url VARCHAR(512)
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id INTEGER PRIMARY KEY,
                    employer_id INTEGER NOT NULL,
                    vacancy_name VARCHAR(255) NOT NULL,
                    salary INTEGER,
                    url VARCHAR(512),
                    FOREIGN KEY (employer_id)
                        REFERENCES employers (employer_id)
                        ON DELETE CASCADE
                );
                """
            )
        conn.commit()
        print("Таблицы employers и vacancies успешно созданы.")
    finally:
        conn.close()