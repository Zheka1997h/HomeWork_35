import logging
from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
import requests

logger = logging.getLogger(__name__)


# --- Вспомогательные функции для API ---
def get_currency_rates(currencies: List[str]) -> List[Dict[str, float]]:
    """Получает курсы валют."""
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=RUB", timeout=5)
        response.raise_for_status()
        data = response.json()
        rates = []
        for cur in currencies:
            rate = 1 / data["rates"].get(cur, 1 / 75.0)
            rates.append({"currency": cur, "rate": round(rate, 2)})
        return rates
    except Exception as e:
        logger.warning(f"Ошибка API валют: {e}. Используем моковые данные.")
        return [{"currency": "USD", "rate": 75.50}, {"currency": "EUR", "rate": 82.30}]


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """Получает цены акций."""
    try:
        prices = []
        for stock in stocks:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}?interval=1d&range=1d"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            price = resp.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
            prices.append({"stock": stock, "price": round(float(price), 2)})
        return prices
    except Exception as e:
        logger.warning(f"Ошибка API акций: {e}. Используем моковые данные.")
        return [{"stock": s, "price": 150.00} for s in stocks]


def get_greeting(dt: datetime) -> str:
    hour = dt.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    if 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


# --- Главная страница ---
def get_main_page_data(date_str: str, df: pd.DataFrame, settings: dict) -> dict:
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_date = dt.replace(day=1, hour=0, minute=0, second=0)

    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= dt)
    filtered_df = df[mask]

    greeting = get_greeting(dt)

    # Данные по картам (используем Сумма платежа — она в валюте счёта)
    cards_data = []
    if "Номер карты" in filtered_df.columns:
        expenses_df = filtered_df[filtered_df["Сумма платежа"] < 0]
        for card, group in expenses_df.groupby("Номер карты"):
            if not card or card == "nan":  # пропускаем пустые карты
                continue
            total_spent = abs(group["Сумма платежа"].sum())
            cashback = round(total_spent * 0.01, 2)
            cards_data.append({"last_digits": card, "total_spent": round(total_spent, 2), "cashback": cashback})

    # Топ-5 транзакций
    top_trans_df = filtered_df.copy()
    top_trans_df["abs_amount"] = top_trans_df["Сумма платежа"].abs()
    top_5 = top_trans_df.nlargest(5, "abs_amount")
    top_transactions = []
    for _, row in top_5.iterrows():
        top_transactions.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": round(row["Сумма платежа"], 2),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    currency_rates = get_currency_rates(settings.get("user_currencies", []))
    stock_prices = get_stock_prices(settings.get("user_stocks", []))

    return {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }


# --- Страница События ---
def get_events_page_data(date_str: str, df: pd.DataFrame, settings: dict, period: str = "M") -> dict:
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    if period == "W":
        start_date = dt - timedelta(days=dt.weekday())
    elif period == "M":
        start_date = dt.replace(day=1)
    elif period == "Y":
        start_date = dt.replace(month=1, day=1)
    else:
        start_date = df["Дата операции"].min()

    start_date = start_date.replace(hour=0, minute=0, second=0)
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= dt)
    filtered_df = df[mask]

    # Расходы
    expenses_df = filtered_df[filtered_df["Сумма платежа"] < 0].copy()
    total_expenses = int(abs(expenses_df["Сумма платежа"].sum()))

    main_exp_cats = expenses_df[~expenses_df["Категория"].isin(["Переводы", "Наличные"])]
    cat_sums = main_exp_cats.groupby("Категория")["Сумма платежа"].sum().abs().sort_values(ascending=False)

    main_expenses = []
    other_sum = 0
    for i, (cat, amount) in enumerate(cat_sums.items()):
        if i < 7:
            main_expenses.append({"category": cat, "amount": int(amount)})
        else:
            other_sum += amount
    if other_sum > 0:
        main_expenses.append({"category": "Остальное", "amount": int(other_sum)})

    # Переводы и наличные
    trans_cash_df = expenses_df[expenses_df["Категория"].isin(["Переводы", "Наличные"])]
    trans_cash_sums = trans_cash_df.groupby("Категория")["Сумма платежа"].sum().abs().sort_values(ascending=False)
    transfers_and_cash = [{"category": cat, "amount": int(amount)} for cat, amount in trans_cash_sums.items()]

    # Поступления
    income_df = filtered_df[filtered_df["Сумма платежа"] > 0]
    total_income = int(income_df["Сумма платежа"].sum())
    income_cats = income_df.groupby("Категория")["Сумма платежа"].sum().sort_values(ascending=False)
    main_income = [{"category": cat, "amount": int(amount)} for cat, amount in income_cats.items()]

    return {
        "expenses": {"total_amount": total_expenses, "main": main_expenses, "transfers_and_cash": transfers_and_cash},
        "income": {"total_amount": total_income, "main": main_income},
        "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
        "stock_prices": get_stock_prices(settings.get("user_stocks", [])),
    }
