from typing import List, Tuple, Union

import pytest

from src.widget import get_date, mask_account_card


@pytest.fixture
def valid_card_data() -> List[Tuple[str, str]]:
    """
    Предоставляет действительные данные карты для тестирования.

    Returns:
        List[Tuple[str, str]]: Предоставляет действительные данные карты для тестирования.Список
        кортежей с информацией о карте и ожидаемым замаскированным результатом.
    """
    return [
        ("Visa 1234567812345678", "Visa 1234 56 ** 5678"),
        ("MasterCard 9876543210123456", "MasterCard 9876 54 ** 3456"),
        ("Maestro 1234567890123456", "Maestro 1234 56 ** 3456"),
        ("Счет 123456789012", "Счет **9012"),
    ]


@pytest.fixture
def invalid_card_data() -> List[str]:
    """
    Предоставляет неверные данные карты для тестирования.

    Returns:
        List[str]: Список строк, представляющих недействительные данные карты.
    """
    return [
        "InvalidType 12345678",  # Неподдерживаемый тип карты
        "Visa 123",  # Слишком короткий номер карты
        "MasterCard 123456789012345",  # Слишком короткий номер MasterCard
    ]


@pytest.fixture
def valid_date_data() -> List[Tuple[str, str]]:
    """
    Предоставляет действительные данные о дате для тестирования.

    Returns:
        List[Tuple[str, str]]: Список кортежей со строками дат и ожидаемым форматированным выводом.
    """
    return [
        ("2023-10-15", "15.10.2023"),
        ("2020-01-01", "01.01.2020"),
    ]


@pytest.fixture
def invalid_date_data() -> List[Union[str, int]]:
    """
    Предоставляет неверные данные о дате для тестирования.

    Returns:
        List[Union[str, int]]: Список недопустимых форматов и типов дат.
    """
    return [
        "2023/10/15",  # Неправильный формат даты
        "15-10-2023",  # Неправильный формат даты
        12345,  # Не строка
        "2023-10-151",  # Некорректная дата
    ]


def test_mask_account_card(valid_card_data: List[Tuple[str, str]]) -> None:
    """
    Проверяет функцию mask_account_card с действительными данными карты.

    Args:
        valid_card_data (List[Tuple[str, str]]): Список действительных данных карты.
    """
    for card_info, expected in valid_card_data:
        assert mask_account_card(card_info) == expected


def test_mask_account_card_invalid(invalid_card_data: List[str]) -> None:
    """
    Проверяет функцию mask_account_card с неверными данными карты.

    Args:
        invalid_card_data (List[str]): Список недействительных данных карты.
    """
    for card_info in invalid_card_data:
        with pytest.raises(ValueError):
            mask_account_card(card_info)


def test_get_date(valid_date_data: List[Tuple[str, str]]) -> None:
    """
    Проверяет функцию get_date с действительными данными о дате.

    Args:
        valid_date_data (List[Tuple[str, str]]): Список действительных данных о датах.
    """
    for date_str, expected in valid_date_data:
        assert get_date(date_str) == expected


def test_get_date_invalid(invalid_date_data: List[Union[str, int]]) -> None:
    """
    Проверяет функцию get_date с неверными данными о дате.

    Args:
        invalid_date_data (List[Union[str, int]]): Список недопустимых форматов и типов дат.
    """
    for date_str in invalid_date_data:
        with pytest.raises(ValueError):
            get_date(str(date_str))


def test_mask_account_card_no_card_type_or_number() -> None:
    with pytest.raises(ValueError, match="Input must contain both card type and card number"):
        mask_account_card("")  # Пустая строка

    with pytest.raises(ValueError, match="Input must contain both card type and card number"):
        mask_account_card("Visa ")  # Только тип карты


def test_invalid_card_type() -> None:
    with pytest.raises(ValueError):
        mask_account_card("Visa123490123456")


def test_mask_account_card_invalid_length() -> None:
    """
    Тест проверяет, что функция mask_account_card выбрасывает ValueError
    с сообщением 'Invalid card number length' для неподдерживаемой длины номера карты
    (не 16 цифр для Visa/MasterCard/Maestro).
    """
    # Тестовые данные: карты с некорректной длиной номера
    test_cases = [
        "Visa 1234567890123",      # 13 цифр
        "MasterCard 123456789012",   # 12 цифр
        "Maestro 123456789012345",  # 15 цифр
        "Visa 12345678901234567",  # 17 цифр
    ]

    for card_info in test_cases:
        with pytest.raises(ValueError) as exc_info:
            mask_account_card(card_info)

        # Проверяем, что сообщение об ошибке именно то, которое мы ожидаем
        assert str(exc_info.value) == "Invalid card number length"


def test_check_card_invalid_length_type() -> None:
    card_type = "Счет"
    with pytest.raises(ValueError):
        mask_account_card(card_type)


def test_check_card_invalid_length_number() -> None:
    card_number = "123"
    with pytest.raises(ValueError):
        mask_account_card(card_number)
