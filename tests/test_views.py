from datetime import datetime
from unittest.mock import patch

import pandas as pd

from src.views import get_events_page_data, get_greeting, get_main_page_data


def test_get_greeting():
    assert get_greeting(datetime(2021, 1, 1, 8)) == "Доброе утро"
    assert get_greeting(datetime(2021, 1, 1, 14)) == "Добрый день"
    assert get_greeting(datetime(2021, 1, 1, 20)) == "Добрый вечер"
    assert get_greeting(datetime(2021, 1, 1, 2)) == "Доброй ночи"


@patch("src.views.get_currency_rates", return_value=[{"currency": "USD", "rate": 75.0}])
@patch("src.views.get_stock_prices", return_value=[{"stock": "AAPL", "price": 150.0}])
def test_get_main_page_data(mock_stocks, mock_rates):
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2021-12-20 10:00:00"]),
            "Номер карты": ["1234"],
            "Сумма платежа": [-100.5],
            "Категория": ["Еда"],
            "Описание": ["Магазин"],
        }
    )
    res = get_main_page_data("2021-12-20 14:30:00", df, {"user_currencies": ["USD"], "user_stocks": ["AAPL"]})
    assert res["greeting"] == "Добрый день"
    assert len(res["cards"]) == 1
    assert len(res["top_transactions"]) == 1


@patch("src.views.get_currency_rates", return_value=[])
@patch("src.views.get_stock_prices", return_value=[])
def test_get_events_page_data(mock_stocks, mock_rates):
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2021-12-20 10:00:00", "2021-12-20 11:00:00"]),
            "Сумма платежа": [-100, 200],
            "Категория": ["Еда", "Зарплата"],
        }
    )
    res = get_events_page_data("2021-12-20 14:30:00", df, {}, period="M")
    assert res["expenses"]["total_amount"] == 100
    assert res["income"]["total_amount"] == 200
