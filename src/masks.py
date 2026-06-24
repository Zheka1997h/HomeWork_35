import logging
import os

os.makedirs("logs", exist_ok=True)
logger_masks = logging.getLogger("masks")
logger_masks.setLevel(logging.DEBUG)
file_handler_masks = logging.FileHandler("logs/masks.log", mode="w", encoding="utf-8")
file_formatter_masks = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler_masks.setFormatter(file_formatter_masks)
logger_masks.addHandler(file_handler_masks)


def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    Args:
        card_number (str): Номер карты (16 цифр).
    Returns
        str: Замаскированный номер в формате XXXX XX** **** XXXX
    """
    logger_masks.info("Начало работы функции get_mask_card_number")
    logger_masks.debug(f"Входные данные: {card_number!r}")

    try:
        if len(card_number) != 16:
            # Логирование ошибочного случая (уровень ERROR)
            logger_masks.error(
                f"Невалидный номер карты: {card_number!r}. " f"Длина: {len(card_number)}, ожидалось: 16"
            )
            raise ValueError("Невалидный номер карты")

        mask = f"{card_number[:4]} {card_number[4:6]} ** **** {card_number[-4:]}"
        logger_masks.info(f"Номер карты успешно замаскирован: {mask}")
        logger_masks.debug(f"Результат маскирования: {mask}")

        return mask

    except ValueError as e:
        logger_masks.error(f"Ошибка при маскировании номера карты: {e}")
        raise


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер банковского счета
    Args:
        account_number(str): Номер счета (20 цифр)
    Returns
        str: Замаскированный счет в формате **XXXX (видны последние 4 цифры)
    """
    logger_masks.info("Начало работы функции get_mask_account")
    logger_masks.debug(f"Входные данные: {account_number!r}")

    try:
        if len(account_number) < 20:
            logger_masks.error(
                f"Невалидный номер счета: {account_number!r}. " f"Длина: {len(account_number)}, минимум: 20"
            )
            raise ValueError("Невалидный номер счета")

        mask = f"**{account_number[-4:]}"
        logger_masks.info(f"Номер счета успешно замаскирован: {mask}")
        logger_masks.debug(f"Результат маскирования: {mask}")

        return mask

    except ValueError as e:
        logger_masks.error(f"Ошибка при маскировании номера счета: {e}")
        raise


if __name__ == "__main__":
    print("Запуск модуля masks...")
    print("\n=== Успешные случаи ===")
    print(get_mask_card_number("1234567890123456"))
    print(get_mask_account("12345678901234567890"))
    print("\n=== Ошибочные случаи ===")
    try:
        get_mask_card_number("12345")
    except ValueError as e:
        print(f"Ожидаемая ошибка: {e}")

    try:
        get_mask_account("123")
    except ValueError as e:
        print(f"Ожидаемая ошибка: {e}")

    print("\n✅ Проверьте файл logs/masks.log")
