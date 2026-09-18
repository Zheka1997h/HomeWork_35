"""Модуль конфигурации для работы с БД и API."""

import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# .strip() автоматически удаляет случайные пробелы и переносы строк
DB_HOST = os.getenv("DB_HOST", "localhost").strip()
DB_PORT = os.getenv("DB_PORT", "5432").strip()
DB_NAME = os.getenv("DB_NAME", "hh_vacancies").strip()
DB_USER = os.getenv("DB_USER", "postgres").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres").strip()

# Параметры по умолчанию для создания БД
DEFAULT_DB_NAME = "postgres"

# Список компаний для парсинга (ID и названия)
COMPANIES = [
    {"id": 3037, "name": "Яндекс"},
    {"id": 2180, "name": "Сбер"},
    {"id": 2733, "name": "МТС"},
    {"id": 2887, "name": "Ростелеком"},
    {"id": 2925, "name": "Тинькофф"},
    {"id": 3778, "name": "VK"},
    {"id": 15478, "name": "Wildberries"},
    {"id": 2180, "name": "Ozon"}, # Примечание: ID Ozon лучше проверить на hh.ru, иногда меняются
    {"id": 2746417, "name": "Kaspersky"},
    {"id": 10000, "name": "HeadHunter"}, # ID hh.ru как работодателя
]