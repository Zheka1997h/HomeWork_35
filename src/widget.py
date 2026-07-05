# -*- coding: utf-8 -*-
from src.decorators import log


@log()
def mask_account_card(card_info: str) -> str:
    """Маскирует номер карты в зависимости от типа карты."""
    parts = card_info.split()

    if len(parts) < 2:
        raise ValueError("Input must contain both card type and card number")

    card_type = parts[0]
    card_number = "".join(filter(str.isdigit, parts[1]))

    if card_type not in ["Visa", "MasterCard", "Maestro", "Счет"]:
        raise ValueError("Unsupported card type")

    if len(card_number) < 4:
        raise ValueError("Card number is too short")

    if card_type in ["Visa", "MasterCard", "Maestro"]:
        if len(card_number) == 16:
            return f"{card_type} {card_number[:4]} {card_number[4:6]} ** {card_number[-4:]}"
    elif card_type == "Счет":
        return f"{card_type} **{card_number[-4:]}"

    raise ValueError("Invalid card number length")


@log()
def get_date(date_str: str) -> str:
    """Преобразует строку даты в формате ISO в ДД.ММ.ГГГГ."""
    if not isinstance(date_str, str) or len(date_str) != 10:
        raise ValueError("Invalid date format")

    from datetime import datetime

    date_obj = datetime.fromisoformat(date_str)
    return date_obj.strftime("%d.%m.%Y")
