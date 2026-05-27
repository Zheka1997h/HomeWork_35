def mask_account_card(card_info: str) -> str:
    parts = card_info.split()
    card_type = " ".join(parts[:-1])
    card_number = parts[-1]

    if card_type.lower() in ["visa", "mastercard", "maestro"]:
        # Маскировка для карт
        masked_number = f"{card_number[:4]} {card_number[4:6]} ** {card_number[-4:]}"
        return f"{card_type} {masked_number}"
    elif card_type.lower() == "счет":
        # Маскировка для счета
        masked_number = f"**{card_number[-4:]}"
        return f"{card_type} {masked_number}"
    else:
        raise ValueError("Неподдерживаемый тип карты или счета")


def get_date(date_str: str) -> str:
    from datetime import datetime

    # Парсим строку даты и возвращаем в нужном формате
    date_obj = datetime.fromisoformat(date_str)
    return date_obj.strftime("%d.%m.%Y")