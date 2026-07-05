# -*- coding: utf-8 -*-
import pytest

from src.masks import get_mask_account, get_mask_card_number


def test_get_mask_card_number() -> None:
    """
    Тестирует функцию get_mask_card_number.

    Проверяет:
    - Корректность маскирования номера карты.
    - Обработку некорректного ввода (слишком короткий номер).
    """
    # Проверка корректного маскирования
    assert get_mask_card_number("1234567812345678") == "1234 56 ** **** 5678"
    # Проверка на некорректный ввод
    with pytest.raises(ValueError):
        get_mask_card_number("1234")  # Слишком короткий номер


def test_get_mask_account() -> None:
    """
    Тестирует функцию get_mask_account.

    Проверяет:
    - Корректность маскирования номера счета.
    - Обработку некорректного ввода (слишком короткий номер).
    """
    assert get_mask_account("12345678901234567890") == "**7890"
    # Проверка на некорректный ввод
    with pytest.raises(ValueError):
        get_mask_account("***45")  # Слишком короткий номер
