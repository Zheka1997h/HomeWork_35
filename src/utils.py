# -*- coding: utf-8 -*-
import json
import logging
import os
from typing import Any

from src.decorators import log

os.makedirs("logs", exist_ok=True)
logger_utils = logging.getLogger("utils")
logger_utils.setLevel(logging.DEBUG)
logger_utils.propagate = False

if not logger_utils.handlers:
    file_handler_utils = logging.FileHandler("logs/utils.log", mode="a", encoding="utf-8", errors="replace")
    file_formatter_utils = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler_utils.setFormatter(file_formatter_utils)
    logger_utils.addHandler(file_handler_utils)


@log()
def read_json_file(file_path: str) -> list[dict[str, Any]]:
    """Читает JSON файл и возвращает список словарей."""
    logger_utils.info(f"Начало чтения файла: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            logger_utils.info(f"Файл успешно прочитан. Найдено записей: {len(data)}")
            return data
        else:
            logger_utils.warning("Формат данных не соответствует списку.")
            return []

    except json.JSONDecodeError as e:
        logger_utils.error(f"Ошибка формата JSON в файле {file_path}: {e}")
        return []

    except FileNotFoundError as e:
        logger_utils.error(f"Файл не найден: {file_path}. {e}")
        return []

    except Exception as e:
        logger_utils.error(f"Непредвиденная ошибка при работе с {file_path}: {e}")
        return []


if __name__ == "__main__":
    print("Запуск модуля utils...")
    my_data = read_json_file("data/operations.json")
    print(f"Результат: {len(my_data)} записей")
