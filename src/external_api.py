# -*- coding: utf-8 -*-
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

from src.decorators import log

load_dotenv()


@log()
def get_exchange_rate(base_currency: str) -> float:
    """Получает курс валюты относительно RUB через API."""
    api_key: str | None = os.getenv("API")
    if not api_key:
        raise ValueError("API key not found in environment variables")

    url: str = "https://api.apilayer.com/exchangerates_data/latest"
    params: Dict[str, str] = {"base": base_currency, "symbols": "RUB"}
    headers: Dict[str, str] = {"apikey": api_key}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    data: Dict[str, Any] = response.json()
    return float(data["rates"]["RUB"])


@log()
def convert_transaction_to_rub(transaction: Dict[str, Any]) -> float:
    """Конвертирует транзакцию в рубли."""
    operation_amount = transaction.get("operationAmount", {})
    amount_str = operation_amount.get("amount", "0")
    currency_info = operation_amount.get("currency", {})
    currency_code = currency_info.get("code", "RUB")

    amount = float(amount_str)

    if currency_code == "RUB":
        return amount
    elif currency_code in ("USD", "EUR"):
        rate: float = get_exchange_rate(currency_code)
        return round(amount * rate, 2)

    return 0.0
