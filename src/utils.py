import json
from typing import Any


def read_json_file(file_path: str) -> list[dict[str, Any]]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        else:
            return []
    except json.JSONDecodeError:
        print("Пустой файл")
        return []
    except FileNotFoundError:
        print("Файл не найден")
        return []
    except Exception:
        print("Ошибка данных !!! ")
        return []  # Исправлено: возвращаем пустой список вместо неопределенной data


if __name__ == "__main__":
    my_data = read_json_file(r"/data/operations.json")
