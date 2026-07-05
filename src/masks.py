# -*- coding: utf-8 -*-
import logging
import os

from src.decorators import log

os.makedirs("logs", exist_ok=True)
logger_masks = logging.getLogger("masks")
logger_masks.setLevel(logging.DEBUG)
logger_masks.propagate = False

if not logger_masks.handlers:
    file_handler_masks = logging.FileHandler("logs/masks.log", mode="a", encoding="utf-8", errors="replace")
    file_formatter_masks = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler_masks.setFormatter(file_formatter_masks)
    logger_masks.addHandler(file_handler_masks)


@log()
def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер банковской карты (16 цифр)."""
    logger_masks.info("Начало работы get_mask_card_number")
    logger_masks.debug(f"Входные данные: {card_number!r}")

    try:
        if len(card_number) != 16:
            logger_masks.error(f"Невалидный номер карты: {card_number!r}. Длина: {len(card_number)}, ожидалось: 16")
            raise ValueError("Невалидный номер карты")

        mask = f"{card_number[:4]} {card_number[4:6]} ** **** {card_number[-4:]}"
        logger_masks.info(f"Номер карты успешно замаскирован: {mask}")
        return mask

    except ValueError as e:
        logger_masks.error(f"Ошибка при маскировании номера карты: {e}")
        raise


@log()
def get_mask_account(account_number: str) -> str:
    """Маскирует номер банковского счета (20 цифр)."""
    logger_masks.info("Начало работы get_mask_account")
    logger_masks.debug(f"Входные данные: {account_number!r}")

    try:
        if len(account_number) < 20:
            logger_masks.error(
                f"Невалидный номер счета: {account_number!r}. Длина: {len(account_number)}, минимум: 20"
            )
            raise ValueError("Невалидный номер счета")

        mask = f"**{account_number[-4:]}"
        logger_masks.info(f"Номер счета успешно замаскирован: {mask}")
        return mask

    except ValueError as e:
        logger_masks.error(f"Ошибка при маскировании номера счета: {e}")
        raise


if __name__ == "__main__":
    print("Запуск модуля masks...")
    print(get_mask_card_number("1234567890123456"))
    print(get_mask_account("12345678901234567890"))
