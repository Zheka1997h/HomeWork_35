import logging
from typing import Any, Dict, List

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def read_excel_data(file_path: str) -> pd.DataFrame:
    """Считывает данные из Excel и возвращает DataFrame."""
    try:
        df = pd.read_excel(file_path)

        # Фильтруем только успешные транзакции
        df = df[df["Статус"] == "OK"].copy()

        # Парсим дату операции (с временем)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

        # Заполняем пропуски
        df["Описание"] = df["Описание"].fillna("")
        df["Категория"] = df["Категория"].fillna("Неизвестно")
        df["Номер карты"] = df["Номер карты"].fillna("")

        # Очищаем номер карты от звёздочки
        df["Номер карты"] = df["Номер карты"].astype(str).str.replace("*", "", regex=False)

        # Приводим числовые колонки к float
        df["Сумма операции"] = pd.to_numeric(df["Сумма операции"], errors="coerce").fillna(0)
        df["Сумма платежа"] = pd.to_numeric(df["Сумма платежа"], errors="coerce").fillna(0)
        df["Кэшбэк"] = pd.to_numeric(df["Кэшбэк"], errors="coerce").fillna(0)

        logger.info(f"Успешно загружено {len(df)} транзакций из {file_path}")
        return df
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        return pd.DataFrame()


def df_to_list_of_dicts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Конвертирует DataFrame в список словарей для сервисов."""
    df_copy = df.copy()
    if "Дата операции" in df_copy.columns:
        df_copy["Дата операции"] = df_copy["Дата операции"].dt.strftime("%d.%m.%Y")
    return df_copy.to_dict(orient="records")
