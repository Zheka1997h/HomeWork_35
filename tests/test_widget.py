import pytest
from src.widget import mask_account_card, get_date  # Замените 'your_module' на имя вашего модуля


@pytest.fixture
def valid_card_data():
    return [
        ("Visa 1234567812345678", "Visa 1234 56 ** 5678"),
        ("MasterCard 9876543210123456", "MasterCard 9876 54 ** 3456"),
        ("Maestro 1234567890123456", "Maestro 1234 56 ** 3456"),
        ("Счет 123456789012", "Счет **9012")
    ]


@pytest.fixture
def invalid_card_data():
    return [
        ("InvalidType 12345678"),   # Неподдерживаемый тип карты
        ("Visa 123"),                 # Слишком короткий номер карты
        ("MasterCard 123456789012345"),]


@pytest.fixture
def valid_date_data():
    return [
        ("2023-10-15", "15.10.2023"),
        ("2020-01-01", "01.01.2020"),
    ]


@pytest.fixture
def invalid_date_data():
    return [
        ("2023/10/15"),  # Неправильный формат даты
        ("15-10-2023"),  # Неправильный формат даты
        (12345),          # Не строка
        ("2023-10-151"),]


def test_mask_account_card(valid_card_data):
    for card_info, expected in valid_card_data:
        assert mask_account_card(card_info) == expected


def test_mask_account_card_invalid(invalid_card_data):
    for card_info in invalid_card_data:
        with pytest.raises(ValueError):
            mask_account_card(card_info)


def test_get_date(valid_date_data):
    for date_str, expected in valid_date_data:
        assert get_date(date_str) == expected


def test_get_date_invalid(invalid_date_data):
    for date_str in invalid_date_data:
        with pytest.raises(ValueError):
            get_date(date_str)
