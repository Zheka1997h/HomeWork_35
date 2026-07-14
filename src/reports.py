import logging
from datetime import datetime
from functools import wraps
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def save_report_to_file(default_filename: str = "report.csv"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result_df = func(*args, **kwargs)
            filename = kwargs.get("filename", default_filename)

            if isinstance(result_df, pd.DataFrame):
                result_df.to_csv(filename, index=False, encoding="utf-8-sig")
                logger.info(f"Отчет успешно сохранен в {filename}")
            else:
                logger.warning("Результат функции не является DataFrame, сохранение пропущено.")
            return result_df

        return wrapper

    return decorator


@save_report_to_file("spending_by_category.csv")
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None, filename: str = "spending_by_category.csv"
) -> pd.DataFrame:
    """Траты по заданной категории за последние 3 месяца."""
    dt = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    start_date = dt - pd.DateOffset(months=3)

    mask = (
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= dt)
        & (transactions["Категория"] == category)
        & (transactions["Сумма платежа"] < 0)
    )

    filtered = transactions[mask].copy()
    filtered["Сумма платежа"] = filtered["Сумма платежа"].abs()

    filtered["Месяц"] = filtered["Дата операции"].dt.to_period("M")
    result = filtered.groupby("Месяц")["Сумма платежа"].sum().reset_index()
    result.rename(columns={"Сумма платежа": "total_spent"}, inplace=True)
    return result


@save_report_to_file("spending_by_weekday.csv")
def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None, filename: str = "spending_by_weekday.csv"
) -> pd.DataFrame:
    """Средние траты по дням недели за последние 3 месяца."""
    dt = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    start_date = dt - pd.DateOffset(months=3)

    mask = (
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= dt)
        & (transactions["Сумма платежа"] < 0)
    )

    filtered = transactions[mask].copy()
    filtered["Сумма платежа"] = filtered["Сумма платежа"].abs()
    filtered["День недели"] = filtered["Дата операции"].dt.day_name()

    result = filtered.groupby("День недели")["Сумма платежа"].mean().reset_index()
    result.rename(columns={"Сумма платежа": "avg_spent"}, inplace=True)

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result["День недели"] = pd.Categorical(result["День недели"], categories=days_order, ordered=True)
    return result.sort_values("День недели")


@save_report_to_file("spending_by_workday.csv")
def spending_by_workday(
    transactions: pd.DataFrame, date: Optional[str] = None, filename: str = "spending_by_workday.csv"
) -> pd.DataFrame:
    """Средние траты в рабочий и выходной день за последние 3 месяца."""
    dt = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    start_date = dt - pd.DateOffset(months=3)

    mask = (
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= dt)
        & (transactions["Сумма платежа"] < 0)
    )

    filtered = transactions[mask].copy()
    filtered["Сумма платежа"] = filtered["Сумма платежа"].abs()

    filtered["Тип дня"] = filtered["Дата операции"].dt.dayofweek.apply(lambda x: "Рабочий" if x < 5 else "Выходной")

    result = filtered.groupby("Тип дня")["Сумма платежа"].mean().reset_index()
    result.rename(columns={"Сумма платежа": "avg_spent"}, inplace=True)
    return result
