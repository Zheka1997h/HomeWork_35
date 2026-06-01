from src.widget import mask_account_card, get_date

import pytest , unittest


class TestMaskAccountCard(unittest.TestCase):

    def test_mask_visa(self):
        self.assertEqual(mask_account_card("Visa 1234567812345678"), "Visa 1234 56 ** 5678")

    def test_mask_mastercard(self):
        self.assertEqual(mask_account_card("MasterCard 9876543210987654"), "MasterCard 9876 54 ** 7654")

    def test_mask_maestro(self):
        self.assertEqual(mask_account_card("Maestro 1111222233334444"), "Maestro 1111 22 ** 4444")

    def test_mask_schet(self):
        self.assertEqual(mask_account_card("Счет 1234567890123456"), "Счет **3456")

    def test_invalid_card_type(self):
        with self.assertRaises(ValueError):
            mask_account_card("UnknownType 1234567890123456")

    def test_invalid_card_number_length(self):
        with self.assertRaises(IndexError):  # Или ValueError, если обработка будет добавлена
            mask_account_card("")  # Неправильная длина номера карты

    def test_invalid_account_number(self):
        with self.assertRaises(IndexError):  # Или ValueError, если обработка будет добавлена
            mask_account_card("")  # Неправильный формат ввода



def test_get_date():
    assert get_date("2023-10-01") == "01.10.2023"
    assert get_date("2022-12-31") == "31.12.2022"

    with pytest.raises(ValueError):
        get_date("31/12/2022")

# Запуск тестов (если этот файл запускается напрямую)
if __name__ == "__main__":
    pytest.main()

