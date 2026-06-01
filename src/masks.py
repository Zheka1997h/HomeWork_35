

def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    Args:
        card_number (str): Номер карты (16 цифр).

    Returns
        str: Замаскированный номер в формате XXXX XX** **** XXXX
    """
    if len(card_number) != 16:
        raise ValueError("Невалидный номер карты")
    mask = f"{card_number[:4]} {card_number[4:6]} ** **** {card_number[-4:]}"
    return mask


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер банковского счета
    Args:
        account_number(str): Номер счета (20 цифр)
    Returns
        str: Замаскированный счет в формате **XXXX (видны последние 4 цифры)
    """
    if len(account_number) < 20:
        raise ValueError("Невалидный номер счета")
    mask = f"**{account_number[-4:]}"
    return mask


