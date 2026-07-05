# -*- coding: utf-8 -*-
import csv
from typing import Any, cast
from zipfile import BadZipFile

import pandas as pd

from src.decorators import log


@log()
def transactions(file_reads: str) -> list[dict[str, Any]]:
    """Читает CSV файл и возвращает список словарей."""
    try:
        with open(file_reads, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            data = list(reader)
        if not data:
            return []
        return data
    except FileNotFoundError:
        print("Неверный путь файла")
        return []
    except UnicodeDecodeError:
        print("Неверный формат кодировки файла")
        return []


@log()
def transactions_ecxel(path_file: str) -> list[dict[str, Any]]:
    """Читает Excel файл и возвращает список словарей."""
    try:
        excel_file = pd.read_excel(path_file)
        return cast(list[dict[str, Any]], excel_file.to_dict(orient="records"))
    except FileNotFoundError:
        print("Файл не найден")
        return []
    except PermissionError:
        print("Нет доступа к файлу")
        return []
    except BadZipFile:
        print("Файл поврежден")
        return []
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return []
