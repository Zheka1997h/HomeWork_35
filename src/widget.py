def mask_account_card(card_info: str) -> str:
    """
    Маскирует номер карты в зависимости от типа карты.

    Args:
        card_info (str): Строка, содержащая тип карты и номер карты.

    Returns:
        str: Строка с замаскированным номером карты.

    Raises:
        ValueError: Если введенные данные неверны, тип карты не поддерживается или номер карты слишком короткий.
    """
    # Разделяем строку на части
    parts = card_info.split()

    # Проверяем, что у нас есть как минимум два элемента: тип карты и номер
    if len(parts) < 2:
        raise ValueError("Input must contain both card type and card number")

    card_type = parts[0]
    card_number = ''.join(filter(str.isdigit, parts[1]))

    # Проверяем, что тип карты поддерживается
    if card_type not in ["Visa", "MasterCard", "Maestro", "Счет"]:
        raise ValueError("Unsupported card type")

    # Проверяем длину номера карты
    if len(card_number) < 4:
        raise ValueError("Card number is too short")

    # Маскируем номер карты в зависимости от типа
    if card_type in ["Visa", "MasterCard", "Maestro"]:
        if len(card_number) == 16:
            return f"{card_type} {card_number[:4]} {card_number[4:6]} ** {card_number[-4:]}"
    elif card_type == "Счет":
        # Для счета просто показываем последние 4 цифры
        return f"{card_type} **{card_number[-4:]}"
    raise ValueError("Invalid card number length")


def get_date(date_str: str) -> str:
    """
    Преобразует строку даты в формате ISO в форматированную строку даты.

    Args:
        date_str (str): Строка даты в формате ISO (ГГГГ-ММ-ДД).

    Returns:
        str: Строка даты, отформатированная как ДД.ММ.ГГГГ.

    Raises:
        ValueError: Строка даты, отформатированная как ДД.ММ.ГГГГ.Если введенная строка даты неверна.
    """
    # Проверка на корректность формата даты
    if not isinstance(date_str, str) or len(date_str) != 10:
        raise ValueError()
    # Парсинг строки в объект datetime
    from datetime import datetime
    date_obj = datetime.fromisoformat(date_str)
    return date_obj.strftime("%d.%m.%Y")
